# Build stage - expects build context = repo root (so frontend/ is available)
# Use: docker build -f frontend/Dockerfile .   or Railway with root = repo
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ .
# Build-time API URL for fetch (e.g. empty = relative /api with proxy)
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Serve stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx-default.conf.template /etc/nginx/conf.d/default.conf.template
COPY frontend/nginx.conf /tmp/nginx.conf
COPY frontend/docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

EXPOSE 80
# Run with sh so shebang/CRLF and exec work reliably on Railway
CMD ["sh", "/docker-entrypoint.sh"]
