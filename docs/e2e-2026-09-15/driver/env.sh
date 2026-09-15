export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
export E=/tmp/orchflows-e2e
export FM_HOME=$E/home
export FM_ROOT_OVERRIDE=$E/firstmate
export FM_HERDR_LAB_STATE_DIR=$E/lab
export FM_BACKEND=herdr
export TMPDIR=$E/tmp
export CORE=$FM_HOME/projects/orchflows-home/.local/packages/orchflows-firstmate
[ -f $E/lab/session ] && export HERDR_SESSION=$(cat $E/lab/session)
fm() { bash "$FM_ROOT_OVERRIDE/bin/$1" "${@:2}"; }
cd "$FM_HOME"
