FROM golang:1.14.6-buster

RUN go env -w GOBIN=/go-bin
RUN export PATH=$PATH:/go-bin

# Do not stop the container
ENTRYPOINT ["tail", "-f", "/dev/null"]
