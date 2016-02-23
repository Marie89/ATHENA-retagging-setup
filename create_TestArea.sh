#!/usr/bin/env bash

# ________________________________________________________________________
function _usage() {
    echo "usage $BASH_SOURCE $1 <branch or trunk> [<test area directory>]"
}

function _help() {
    cat <<EOF
Script to make the creation of a Athena test area less painful.

To use it you'll need:
 - Make up your mind if you want to use the trunk or an older branch.
   This is to be specified by an additional argument when sourcing
   this script.

This script will:
 - Set up the required environment variables.
 - Set up Athena in the (to be) specified directory. The path can
   be given as a second argument, otherwise you'll be asked to specify it.
EOF
}

# ________________________________________________________________________
# sanity checks
_files_exist () {
    files=$(shopt -s nullglob dotglob; echo *)
    if (( ${#files} )) ; then
       return 0
    else
  return 1
    fi
}

if [ "$1" != "branch" -a "$1" != "trunk" ]; then
    echo "ERROR: You did not decide on using either the branch or the trunk in your setup.\n"
    _usage
    _help
    return 1
fi

# make aliases from your ~/.bashrc available
shopt -s expand_aliases

# set up ATLAS stuff
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
alias setupATLAS='source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh'

if [[ ! $ATLAS_LOCAL_ASETUP_VERSION ]] ; then
    echo -n "setting up local ATLAS environment..."
    setupATLAS -q
    lsetup asetup
    echo "done"
else
    echo "ATLAS environment is already setup, not setting up again"
fi

# setup directory
if (( $# < 2 )) ; then
   echo "Please enter the directory name (from current directory) in which you want to set up the test area: "
   read TestArea_name
   echo "The test area will be set up in the directory: $PWD/$TestArea_name"
else
    TestArea_name=$2
    echo "The test area will be set up in the directory: $TestArea_path"
fi

mkdir -p $TestArea_name
SRC_DIR=$(pwd)  # come back to this directory later
cd $TestArea_name
if _files_exist $TestArea_name; then
    echo "files exist in $TestArea_name, quitting..."
    cd $SRC_DIR
    return 1
fi

# actually setting up the test area:
# 1. checkout packages
if [[ "$1" == "branch" ]]; then
    asetup 20.1.6.3,AtlasDerivation,gcc48,here,64
    pkgco.py BTagging-00-07-43-branch
    pkgco.py JetTagTools-01-00-56-branch
    pkgco.py JetInterface-00-00-43
    pkgco.py JetMomentTools-00-03-20
    pkgco.py PileupReweighting-00-03-06
elif [[ "$1" == "trunk" ]]; then
    asetup 20.7.3.3,AtlasDerivation,gcc48,here,64
    pkgco.py BTagging-00-07-58
    pkgco.py JetTagTools-01-00-83
    pkgco.py JetMomentTools-00-03-20        # TODO: check if the default version or a more recent one can be used without problems
    pkgco.py PileupReweighting-00-03-06     # TODO: check if the default version or a more recent one can be used without problems
fi
svn co svn+ssh://svn.cern.ch/reps/atlasperf/CombPerf/FlavorTag/FlavourTagPerformanceFramework/trunk/xAODAthena xAODAthena
setupWorkArea.py
# 2. build all the things
(
    cd WorkArea/cmt
    cmt bro cmt config
    cmt bro cmt make
)

# 3. setup run area (convenience)
cd $TestArea
mkdir -p run
if [[ "$1" == "branch" ]]; then
    declare -a files_arr=("jobOptions_Tag.py" "RetagFragment.py")
elif [[ "$1" == "trunk" ]]; then
    declare -a files_arr=("jobOptions_Tag_trunk.py" "RetagFragment.py")
fi
for i in "${files_arr[@]}"; do
    cp $TestArea/xAODAthena/run/$FILE run/.
done

# get default NN configuration file
cp /afs/cern.ch/user/m/malanfer/public/training_files/AGILEPack_b-tagging.weights.json $TestArea/run/.
# link the job options file
cd run/
ln -sf $SRC_DIR/jobOptions_Tag.py

# go back to the directory we started in
cd $SRC_DIR

# cleanup
unset SRC_DIR FILE
