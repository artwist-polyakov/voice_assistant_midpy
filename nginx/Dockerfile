FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/www/static \
    && mkdir -p /var/www/media \
    && mkdir /etc/nginx/ssl

COPY data/ /var/www/static

EXPOSE 80