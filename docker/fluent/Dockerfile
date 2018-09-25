FROM fluent/fluentd:v0.12.28-onbuild

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild MongoDB Logs"


WORKDIR /home/fluent
ENV PATH /home/fluent/.gem/ruby/2.3.0/bin:$PATH

USER root
RUN apk --no-cache --update add sudo && \

    sudo -u fluent gem install fluent-plugin-mongo -v 0.7.15 && \

    rm -rf /home/fluent/.gem/ruby/2.3.0/cache/*.gem && sudo -u fluent gem sources -c && \
    apk del sudo build-base ruby-dev && rm -rf /var/cache/apk/*

RUN apk update && apk add openssh-client

EXPOSE 24284
EXPOSE 27017

USER fluent
RUN mkdir -p ~/.ssh && \
    chmod 0700 ~/.ssh && \
    ssh-keyscan -t rsa 130.226.55.42 >> ~/.ssh/known_hosts

CMD exec fluentd -c /fluentd/etc/$FLUENTD_CONF -p /fluentd/plugins $FLUENTD_OPT