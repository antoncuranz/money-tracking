# build stage
FROM node:lts-alpine as build-stage
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /dist /usr/share/nginx/html

# substitute environment variables before starting nginx
COPY substitute-env-vars.sh /docker-entrypoint.d/99-substitute-env-vars.sh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
