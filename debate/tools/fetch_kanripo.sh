#!/usr/bin/env bash
# Fetch primary-source texts from the Kanseki Repository (kanripo, CC BY-SA 4.0) on GitHub
# into debate/bibliography/local/kanripo/<KR-id>/ . GitHub is reachable from the web sandbox
# even when ctext.org / wikisource are not. Re-run any time; existing clones are skipped.
set -u
cd "$(dirname "$0")/../bibliography/local" || exit 1
mkdir -p kanripo && cd kanripo
REPOS="
KR1e0001 春秋左傳(正文)
KR1e0006 春秋公羊傳注疏
KR1e0008 春秋穀梁傳(正文)
KR1e0122 春秋繁露-董仲舒
KR2a0001 史記-司馬遷
KR2a0007 前漢書-班固
KR2a0009 後漢書-范曄
KR2e0001 國語-韋昭注
KR2e0003 戰國策-高誘注
KR3c0005 韓非子
KR3j0009 呂氏春秋
KR3j0010 淮南鴻烈解
KR1c0066 韓詩外傳
KR3j0080 論衡-王充
KR1j0018 說文解字
KR1g0003 經典釋文-陸德明
KR3a0005 新書-賈誼
"
echo "$REPOS" | while read -r id name; do
  [ -z "$id" ] && continue
  if [ -d "$id/.git" ]; then echo "skip $id ($name)"; continue; fi
  if GIT_TERMINAL_PROMPT=0 git clone -q --depth 1 "https://github.com/kanripo/$id" "$id" 2>/dev/null; then
    echo "ok   $id ($name)"
  else
    echo "FAIL $id ($name)"
  fi
done
