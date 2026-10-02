[app]
title = SHAHADAT RACING
package.name = shahadatracing
package.domain = com.shahadat
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0
requirements = python3==3.11.9,hostpython3==3.11.9,pygame-ce
orientation = portrait
fullscreen = 0
android.hide_statusbar = 1
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 24
android.ndk = 25b
android.permissions = INTERNET
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
