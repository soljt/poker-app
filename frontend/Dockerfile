FROM dhi.io/node:25.8-debian13-dev AS build

WORKDIR /app
COPY . .

# public site key, baked in at build time
ARG VITE_TURNSTILE_SITE_KEY
ENV VITE_TURNSTILE_SITE_KEY=$VITE_TURNSTILE_SITE_KEY

RUN npm install
RUN npm run build

# Nginx stage
FROM dhi.io/nginx:1.29-debian12-dev

# Copy the build output to Nginx's public directory
COPY --from=build /app/dist /usr/share/nginx/html

# Optional: custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
