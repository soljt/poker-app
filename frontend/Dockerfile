FROM node:22-alpine AS build

# Update apk packages to reduce vulnerabilities
RUN apk update && apk upgrade

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

# Nginx stage
FROM nginx:alpine

# Copy the build output to Nginx's public directory
COPY --from=build /app/dist /usr/share/nginx/html

# Optional: custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
