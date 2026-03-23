FROM nginx:1.27-alpine

RUN printf 'server {\n\
    listen 8080;\n\
    root /usr/share/nginx/html;\n\
    location / { try_files $uri $uri/ =404; }\n\
}\n' > /etc/nginx/conf.d/default.conf

COPY shelldash.html /usr/share/nginx/html/index.html
COPY shelldash.js   /usr/share/nginx/html/

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
