$ErrorActionPreference = "Stop"

$expected = "C:\Users\24607\Desktop\项目\DataSpeak"
$current = (Get-Location).Path
if ($current -ne $expected) {
    throw "请先进入 DataSpeak 项目根目录：$expected"
}

conda create -n ds python=3.11 -y
conda activate ds
pip install -r requirements.txt

if ($env:CONDA_DEFAULT_ENV -ne "ds") {
    throw "当前 conda 环境不是 ds，请重新执行：conda activate ds"
}

if ((Split-Path -Leaf $current) -ne "DataSpeak") {
    throw "当前项目路径不是 DataSpeak"
}

Write-Host "DataSpeak conda 环境 ds 已准备完成。"
