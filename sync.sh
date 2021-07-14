#!/usr/bin/env bash

git config user.name "771073216"
git config user.email "771073216@qq.com"

main() {
  xray_local=$(awk '/\<xray\>/ {print$2}' version)
  v2rayn_local=$(awk '/\<v2rayn\>/ {print$2}' version)
  v2rayng_local=$(awk '/v2rayng/ {print$2}' version)
  caddy_local=$(awk '/caddy/ {print$2}' version)
  anxray_local=$(awk '/anxray/ {print$2}' version)
  xray_latest=$(wget -qO- "https://api.github.com/repos/XTLS/Xray-core/tags" | awk -F '"' '/name/ {print $4}' | head -n 1 | tr -d 'v')
  v2rayn_latest=$(wget -qO- "https://api.github.com/repos/2dust/v2rayN/tags" | awk -F '"' '/name/ {print $4}' | head -n 1)
  v2rayng_latest=$(wget -qO- "https://api.github.com/repos/2dust/v2rayNG/tags" | awk -F '"' '/name/ {print $4}' | head -n 1)
  caddy_latest=$(wget -qO- "https://api.github.com/repos/caddyserver/caddy/tags" | awk -F '"' '/name/ {print $4}' | head -n 1 | tr -d 'v')
  anxray_latest=$(wget -qO- "https://api.github.com/repos/XTLS/AnXray/tags" | awk -F '"' '/name/ {print $4}' | head -n 1)
  cat > v2 <<- EOF
xray: $xray_latest
anxray: $anxray_latest
v2rayn: $v2rayn_latest
v2rayng: $v2rayng_latest
caddy: $caddy_latest
EOF
  list=$(diff version v2 | grep '>' | tr -d ' >')
  [[ -z $list ]] && echo "no update" && exit 0
  for file in $list; do
    name=$(echo "$file" | awk -F':' '{print$1}')
    "${name}"_update
  done
  mv v2 version
  git push
}

xray_update() {
  echo "Downloading Xray-linux-64.zip..."
  wget -q https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -O linux/xray-linux.zip || exit 1
  echo "Downloading Xray-windows-64.zip..."
  wget -q https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip -O windows/xray-windows.zip || exit 1
  git add .
  git commit -am "xray: v${xray_local} -> v${xray_latest}"
}

caddy_update() {
  echo "Downloading caddy_'$caddy_latest'_linux_amd64.deb..."
  wget -q https://github.com/caddyserver/caddy/releases/latest/download/caddy_"$caddy_latest"_linux_amd64.deb -O linux/caddy.deb || exit 1
  git add .
  git commit -am "caddy: v${caddy_local} -> v${caddy_latest}"
}

v2rayn_update() {
  rm windows/v2rayn-v"$v2rayn_local".zip windows/v2rayn-core-v"$v2rayn_local".zip
  echo "Downloading v2rayN.zip..."
  wget -q https://github.com/2dust/v2rayN/releases/latest/download/v2rayN.zip -O windows/v2rayn-v"$v2rayn_latest".zip || exit 1
  echo "Downloading v2rayN-Core.zip..."
  wget -q https://github.com/2dust/v2rayN/releases/latest/download/v2rayN-Core.zip -O windows/v2rayn-core-v"$v2rayn_latest".zip || exit 1
  sed -i "s/v2rayn-v$v2rayn_local.zip/v2rayn-v$v2rayn_latest.zip/g" README.md
  sed -i "s/v2rayn-core-v$v2rayn_local.zip/v2rayn-core-v$v2rayn_latest.zip/g" README.md
  git add .
  git commit -am "v2rayn: v${v2rayn_local} -> v${v2rayn_latest}"
}

v2rayng_update() {
  rm android/v2rayng-v"$v2rayng_local".apk
  echo "Downloading v2rayNG_'$v2rayng_latest'_arm64-v8a.apk..."
  wget -q https://github.com/2dust/v2rayNG/releases/download/"$v2rayng_latest"/v2rayNG_"$v2rayng_latest"_arm64-v8a.apk -O android/v2rayng-v"$v2rayng_latest".apk || exit 1
  sed -i "s/v2rayng-v$v2rayng_local.apk/v2rayng-v$v2rayng_latest.apk/g" README.md
  git add .
  git commit -am "v2rayng: v${v2rayng_local} -> v${v2rayng_latest}"
}

anxray_update() {
  rm android/anxray-"$anxray_local".apk
  echo "Downloading AX-'$anxray_latest'-arm64-v8a.apk..."
  wget -q https://github.com/XTLS/AnXray/releases/latest/download/AX-"$anxray_latest"-arm64-v8a.apk -O android/anxray-"$anxray_latest".apk || exit 1
  sed -i "s/anxray-$anxray_local.apk/anxray-$anxray_latest.apk/g" README.md
  git add .
  git commit -am "anxray: ${anxray_local} -> ${anxray_latest}"
}

main
