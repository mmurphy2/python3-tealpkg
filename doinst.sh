# doinst.sh for tealpkg
config() {
  NEW="$1"
  OLD="$(dirname $NEW)/$(basename $NEW .new)"
  # If there's no config file by that name, mv it over:
  if [ ! -r $OLD ]; then
    mv $NEW $OLD
  elif [ "$(cat $OLD | md5sum)" = "$(cat $NEW | md5sum)" ]; then
    # toss the redundant copy
    rm $NEW
  fi
  # Otherwise, we leave the .new copy for the admin to consider...
}

config etc/tealpkg/tealpkg.ini.new
config etc/tealpkg/exclude.list.new
config etc/tealpkg/repos/slackware-main.ini.new
config etc/tealpkg/repos/slackware-extra.ini.new
config etc/tealpkg/repos/slackware-pasture.ini.new
config etc/tealpkg/repos/slackware-patches.ini.new
config etc/tealpkg/repos/slackware-testing.ini.new
config etc/tealpkg/repos/slackware.mirrors.new

if [ -f etc/tealpkg/repos/alienbob-multilib.ini.new ]; then
    config etc/tealpkg/repos/alienbob-multilib.ini.new
    config etc/tealpkg/repos/alienbob.mirrors.new
fi
