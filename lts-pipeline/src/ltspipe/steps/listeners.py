from datetime import datetime
import json
import logging
import os
import time
import traceback
from typing import Any, Callable, List, Optional, Tuple
import websocket  # type: ignore

from ltspipe.messages import Message, MessageSource
from ltspipe.steps.base import StartStep, MidStep


class FileListenerStep(StartStep):
    """
    Listen incoming data from a file or path.
    """

    def __init__(
            self,
            logger: logging.Logger,
            competition_code: str,
            single_file: bool,
            infinite_loop: bool,
            message_source: MessageSource,
            is_json: bool,
            next_step: MidStep,
            on_error: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            competition_code (str): Verbose code to identify the competition.
            single_file (bool): If true, it asks for a path of a file.
                Otherwise, it asks for a path of files.
            infinite_loop (bool): If true, it will keep asking for directory or
                file paths until the process is killed.
            message_source (MessageSource): Message source to mock.
            is_json (bool): If this flag is given, the format of the messages
                must be JSON and it should be same like the Raw Storage works.
                Note: The value message source is ignored with this option.
            next_step (MidStep): The next step to apply to the message.
            on_error (MidStep | None): Optionally, apply another step to the
                message if there is any error on running time.
        """
        self._logger = logger
        self._competition_code = competition_code
        self._single_file = single_file
        self._infinite_loop = infinite_loop
        self._message_source = message_source
        self._is_json = is_json
        self._next_step = next_step
        self._on_error = on_error

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = [self._next_step] + self._next_step.get_children()
        if self._on_error is not None:
            children += [self._on_error] + self._on_error.get_children()
        return children

    def start_step(self) -> None:
        """Start listening the console input."""
        prompt_txt = ('Introduce the file path: ' if self._single_file
                      else 'Introduce the path of files: ')
        first_iteration = True
        while self._infinite_loop or first_iteration:
            file_path = input(prompt_txt)
            if os.path.isdir(file_path):
                # If is directory, retrieve all files in it
                self._step_multi_files(file_path)
            elif os.path.isfile(file_path):
                # Otherwise, read the given file
                self._step_single_file(file_path)
            else:
                # Unknown path
                self._logger.warning('File not detected')
            first_iteration = False

    def _step_multi_files(self, path: str) -> None:
        """Run step with a path of files."""
        files_paths = [os.path.join(path, f) for f in os.listdir(path)
                       if os.path.isfile(os.path.join(path, f))]
        for i, file_path in enumerate(files_paths):
            input(
                f'(Press Enter) File {i + 1} / {len(files_paths)}: {file_path}')
            self._step_single_file(file_path)

    def _step_single_file(self, file_path: str) -> None:
        """Run step with a single file."""
        content, message_source = self._get_path_content(file_path)
        for data in content:
            try:
                msg = Message(
                    competition_code=self._competition_code,
                    data=data,
                    source=message_source,
                    created_at=datetime.utcnow().timestamp(),
                    updated_at=datetime.utcnow().timestamp(),
                )
                self._next_step.run_step(msg)
            except Exception as e:
                self._logger.critical(e, exc_info=True)
                if self._on_error is not None:
                    msg = Message(
                        competition_code=msg.competition_code,
                        data=msg.data,
                        source=msg.source,
                        decoder=msg.decoder,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=str(e),
                        error_traceback=traceback.format_exc(),
                    )
                    msg.updated()
                    self._on_error.run_step(msg)

    def _get_path_content(
            self,
            file_path: str) -> Tuple[List[str], MessageSource]:
        """Read the content of a single file or a whole directory."""
        if self._single_file:
            if not os.path.exists(file_path):
                self._logger.error(f'File does not exist: {file_path}')
                return [], self._message_source
            with open(file_path, 'r') as fp:
                raw_data = fp.read()
                if self._is_json:
                    json_data = json.loads(raw_data)
                    message_source = MessageSource(json_data['source'])
                    data = json_data['data']
                else:
                    message_source = self._message_source
                    data = raw_data
                return [data], message_source
        else:
            raise NotImplementedError  # TODO


class WebsocketListenerStep(StartStep):
    """
    Listen incoming data from a websocket.
    """

    def __init__(
            self,
            logger: logging.Logger,
            competition_code: str,
            uri: str,
            next_step: MidStep,
            on_error: Optional[MidStep]) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            competition_code (str): Verbose code to identify the competition.
            uri (str): websocket URI to get messages from.
            next_step (MidStep): The next step to apply to the message.
            on_error (MidStep | None): Optionally, apply another step to the
                message if there is any error on running time.
        """
        self._logger = logger
        self._competition_code = competition_code
        self._uri = uri
        self._next_step = next_step
        self._on_error = on_error
        self._is_closed = False

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = [self._next_step] + self._next_step.get_children()
        if self._on_error is not None:
            children += [self._on_error] + self._on_error.get_children()
        return children

    def start_step(self) -> None:
        """Start listening the websocket for incoming data."""
        self._is_closed = False
        websocket.enableTrace(True)
        self._logger.debug(f'Websocket: {self._uri}')
        ws = self._build_websocket(
            self._uri,
            on_message=self._on_ws_message,
            on_error=self._on_ws_error,
            on_close=self._on_ws_close,
            on_open=self._on_ws_open)

        while not self._is_closed:
            ws.run_forever()
            time.sleep(1)

    def _on_ws_open(self, ws: websocket.WebSocketApp) -> None:  # noqa: U100
        """Handle open connection event."""
        self._logger.debug('Open websocket connection')

    def _on_ws_close(self, ws: websocket.WebSocketApp) -> None:  # noqa: U100
        """Handle close connection event."""
        self._logger.debug('Close websocket connection')
        self._is_closed = True

    def _on_ws_message(
            self,
            ws: websocket.WebSocketApp,  # noqa: U100
            data: str) -> None:
        """Handle new message event."""
        try:
            data = data.strip()
            if not data:
                self._logger.debug('Websocket data: <empty content>')
                return
            self._logger.info(f'Websocket data: {data}')
            msg = Message(
                competition_code=self._competition_code,
                data=data,
                source=MessageSource.SOURCE_WS_LISTENER,
                created_at=datetime.utcnow().timestamp(),
                updated_at=datetime.utcnow().timestamp(),
            )
            self._next_step.run_step(msg)
        except Exception as e:
            self._logger.critical(e, exc_info=True)
            if self._on_error is not None:
                msg = Message(
                    competition_code=msg.competition_code,
                    data=msg.data,
                    source=msg.source,
                    decoder=msg.decoder,
                    created_at=datetime.utcnow().timestamp(),
                    updated_at=datetime.utcnow().timestamp(),
                    error_description=str(e),
                    error_traceback=traceback.format_exc(),
                )
                msg.updated()
                self._on_error.run_step(msg)

    def _on_ws_error(
            self,
            ws: websocket.WebSocketApp,  # noqa: U100
            error: str) -> None:
        """Handle an error event."""
        self._logger.error(f'Websocket error: {error}')

    def _build_websocket(
            self,
            uri: str,
            on_message: Callable,
            on_error: Callable,
            on_close: Callable,
            on_open: Callable) -> websocket.WebSocketApp:
        """Wrap builder of websocket."""
        return websocket.WebSocketApp(
            uri,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open)
