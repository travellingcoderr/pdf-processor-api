# Build stage - expects build context = repo root (so frontend/ is available)
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ .
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Serve stage: one Node process listening on $PORT (Railway-friendly)
FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/dist ./dist
RUN npm install -g serve

EXPOSE 3000
# Railway injects PORT; default 3000 for local Docker
ENV PORT=3000
CMD ["sh", "-c", "serve -s dist -l ${PORT}"]
