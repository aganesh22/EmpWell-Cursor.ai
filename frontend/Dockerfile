FROM node:20-alpine

WORKDIR /app

COPY package.json ./package.json
RUN npm install

COPY . /app

CMD ["npm", "run", "dev", "--", "--host"]