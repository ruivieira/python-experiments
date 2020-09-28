FROM fedora:32

COPY wax.bin /wax.bin
RUN chmod +x /wax.bin
WORKDIR /
ENTRYPOINT ["/wax.bin"]