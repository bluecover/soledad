FROM lcgc/python:2.7.10-5
MAINTAINER Justin Lee <lijiaqing@licaigc.com>

RUN virtualenv  /opt/solar
ENV VIRTUAL_ENV /opt/solar
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

ENV XDG_CACHE_HOME /cache
ENV NPM_CONFIG_CACHE /cache
VOLUME /cache

ADD . /opt/solar/src
WORKDIR /opt/solar/src
RUN sed -i 's#guihua/pypi#guihua/release#' requirements*.txt
RUN make install-deps
RUN sed -i 's#guihua/release#guihua/pypi#' requirements*.txt
RUN npm run clean
RUN npm run release
