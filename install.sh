#!/bin/bash
requirements=$(cat ./requirements.txt | awk -F'>' '{print $1}')
packages=$(pip list | awk '{print $1}')
lack=''
for pack in $requirements;do
    if grep $pack <(echo $packages) >/dev/null 2>&1 ;then
        continue
    fi
    lack="$lack $pack"
done

if ! [[ $lack =~ ^[[:space:]]*$ ]]; then
    echo '缺少'$lack
    echo '使用"pip install -r ./requirements.txt 安装依赖"'
    exit 1
fi

! [[ -f admin.toml                  ]] && echo 缺少admin.toml             && exit 1
! [[ -f fetch.py                    ]] && echo 缺少fetch.py               && exit 1
! [[ -d files                       ]] && echo 缺少目录files              && exit 1
! [[ -f __init__.py                 ]] && echo 缺少__init__.py            && exit 1
! [[ -f install.sh                  ]] && echo 缺少install.sh             && exit 1
! [[ -d log                         ]] && echo 缺少目录log                && exit 1
! [[ -f mailbot_init.sh             ]] && echo 缺少mailbot_init.sh        && exit 1
! [[ -f mailbot.py                  ]] && echo 缺少mailbot.py             && exit 1
! [[ -f mailbot.service             ]] && echo 缺少mailbot.service        && exit 1
! [[ -f README.md                   ]] && echo 缺少README.md              && exit 1
! [[ -f requirements.txt            ]] && echo 缺少requirements.txt       && exit 1
! [[ -f send_post.py                ]] && echo 缺少send_post.py           && exit 1
! [[ -d test                        ]] && echo 缺少目录test               && exit 1
! [[ -d tmp                         ]] && echo 缺少目录tmp                && exit 1
! [[ -d util                        ]] && echo 缺少目录util               && exit 1
! [[ -f util/authserver.py          ]] && echo 缺少authserver.py          && exit 1
! [[ -d util/functional             ]] && echo 缺少functional             && exit 1
! [[ -f util/functional/__init__.py ]] && echo 缺少functional/__init__.py && exit 1
! [[ -f util/functional/util.py     ]] && echo 缺少functional/util.py     && exit 1


! [[ -r util/handler.py             ]] && echo 缺少handler.py             && exit 1
! [[ -f util/logger.py              ]] && echo 缺少logger.py              && exit 1
! [[ -f util/validate.py            ]] && echo 缺少validate.py            && exit 1

! [[ -e $HOME/.config/systemd/user ]] && mkdir $HOME/.config/systemd/user
cp mailbot.service $HOME/.config/systemd/user/mailbot.service

! [[ -e $HOME/.local/bin/mailbot ]] && mkdir -p $HOME/.local/bin/mailbot
cp -r . $HOME/.local/bin/mailbot

systemctl --user daemon-reload

[[ -z $! ]] && echo '使用systemctl --user start mailbot' 启动服务

exit 0
