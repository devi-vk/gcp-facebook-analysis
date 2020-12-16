FROM nodered/node-red

RUN npm install node-red-contrib-google-cloud

ENTRYPOINT ["npm", "--no-update-notifier", "--no-fund", "start", "--cache", "/data/.npm", "--", "--userDir", "/data"]