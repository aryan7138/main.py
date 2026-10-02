[app]
title = SHAHADAT RACING
package.name = shahadatracing
package.domain = com.shahadat

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = main.py

version = 1.0

requirements = python3,pygame-ce

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Pygame এর জন্য এটা দরকার
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
