FROM rust:latest AS builder

WORKDIR /app

COPY Cargo.toml .
COPY Cargo.lock .
RUN mkdir src && echo "fn main() { println!(\"Debug mode\"); }" > src/main.rs

RUN cargo build --release

COPY src/* src/
# This allows cargo to see it as a newer file
RUN touch src/main.rs

RUN ls .
RUN ls -laF /app
RUN ls -laF /app/target/release
RUN cargo build --release

FROM debian:buster-slim

WORKDIR /app
COPY --from=builder /app/target/release/overcri /app/overcri

CMD ["/app/overcri"]
