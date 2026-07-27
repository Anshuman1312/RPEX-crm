# ── Builder stage ─────────────────────────────────────────────────────
FROM node:22-alpine as builder

ARG VITE_API_URL=http://localhost:8000
ARG ENVIRONMENT=production

WORKDIR /app

ENV VITE_API_URL=${VITE_API_URL}

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci --no-audit

# Copy source code
COPY . .

# Build the application
RUN npm run build

# ── Runtime stage ─────────────────────────────────────────────────────
FROM node:22-alpine

WORKDIR /app

# Install serve to run the application
RUN npm install -g serve

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# Copy built application from builder
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist

# Switch to non-root user
USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["serve", "-s", "dist", "-l", "3000"]
