FROM node:20-alpine
WORKDIR /workspace
COPY package.json .
COPY package-lock.json .
RUN npm install
COPY src/ src/
COPY public/ public/
CMD ["npm", "run", "dev"]
