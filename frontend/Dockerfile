# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY  . .

CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "4200"]
# kubectl port-forward service/frontend-service 9700:80 -n bqnq
# docker run -p 8080:4200 -it frontend:latest sh
# npx ng serve --host 0.0.0.0 --port 4200
