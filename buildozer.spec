[app]

title = Lector Códigos Barras
package.name = barcodescanner
package.domain = org.applector
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.1,pillow,android,pyjnius,oscpy
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.private_storage = True
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.release_artifact = apk
android.debug_artifact = apk

# Python-for-android options
p4a.branch = develop
p4a.extra_args = --enable-androidx

ios.codesign.allowed = false
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
