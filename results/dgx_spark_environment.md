# DGX Spark Environment Snapshot

## Date
Wed Jun 24 03:53:28 AM UTC 2026

## Host
spark-b96e

## Architecture
aarch64

## Kernel
Linux spark-b96e 6.17.0-1021-nvidia #21-Ubuntu SMP PREEMPT_DYNAMIC Wed May 27 19:14:05 UTC 2026 aarch64 aarch64 aarch64 GNU/Linux

## NVIDIA SMI
Tue Jun 23 21:53:28 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.159.03             Driver Version: 580.159.03     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GB10                    On  |   0000000F:01:00.0 Off |                  N/A |
| N/A   46C    P8              3W /  N/A  | Not Supported          |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A            2472      G   /usr/lib/xorg/Xorg                      126MiB |
|    0   N/A  N/A            2817      G   /usr/bin/gnome-shell                     18MiB |
+-----------------------------------------------------------------------------------------+

## NVCC
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2025 NVIDIA Corporation
Built on Wed_Aug_20_01:57:39_PM_PDT_2025
Cuda compilation tools, release 13.0, V13.0.88
Build cuda_13.0.r13.0/compiler.36424714_0

## Conda Environments

# conda environments:
#
# * -> active
# + -> frozen
base                     /home/millersun360/miniforge3
rapids-cuda13        *   /home/millersun360/miniforge3/envs/rapids-cuda13


## RAPIDS Environment Packages
# packages in environment at /home/millersun360/miniforge3/envs/rapids-cuda13:
#
# Name                                Version          Build                              Channel
_openmp_mutex                         4.5              20_gnu                             conda-forge
_python_abi3_support                  1.0              hd8ed1ab_2                         conda-forge
arm-variant                           1.2.0            sbsa                               conda-forge
aws-c-auth                            0.10.3           h5c394e5_3                         conda-forge
aws-c-cal                             0.9.14           h343fa25_2                         conda-forge
aws-c-common                          0.14.0           he30d5cf_0                         conda-forge
aws-c-compression                     0.3.2            h5b0efec_2                         conda-forge
aws-c-event-stream                    0.7.1            h70cbb06_2                         conda-forge
aws-c-http                            0.11.0           h9bcd1b7_2                         conda-forge
aws-c-io                              0.26.3           hacd6ab7_5                         conda-forge
aws-c-mqtt                            0.16.0           h3479d1b_0                         conda-forge
aws-c-s3                              0.12.6           hdd40dfe_0                         conda-forge
aws-c-sdkutils                        0.2.5            h5b0efec_0                         conda-forge
aws-checksums                         0.2.10           h5b0efec_2                         conda-forge
aws-crt-cpp                           0.40.1           h0495e26_1                         conda-forge
aws-sdk-cpp                           1.11.833         h6aa9b71_7                         conda-forge
azure-core-cpp                        1.16.3           h412bcfc_0                         conda-forge
azure-identity-cpp                    1.13.3           hd0001b6_2                         conda-forge
azure-storage-blobs-cpp               12.18.0          h2e50874_1                         conda-forge
azure-storage-common-cpp              12.14.0          hacd5e5f_1                         conda-forge
azure-storage-files-datalake-cpp      12.16.0          hde34f15_1                         conda-forge
bzip2                                 1.0.8            h4777abc_9                         conda-forge
c-ares                                1.34.6           he30d5cf_0                         conda-forge
ca-certificates                       2026.6.17        hbd8a1cb_0                         conda-forge
cachetools                            7.1.4            pyhd8ed1ab_0                       conda-forge
cpython                               3.12.13          py312hd8ed1ab_0                    conda-forge
cuda-bindings                         13.3.0           py312hf55c4e8_2                    conda-forge
cuda-cccl_linux-aarch64               13.0.85          h579c4fd_0                         conda-forge
cuda-core                             0.7.0            cuda13_py312h92e596d_0             conda-forge
cuda-crt-dev_linux-aarch64            13.0.88          h579c4fd_0                         conda-forge
cuda-crt-tools                        13.0.88          h579c4fd_0                         conda-forge
cuda-cudart                           13.0.96          h8f3c8d4_0                         conda-forge
cuda-cudart-dev                       13.0.96          h8f3c8d4_0                         conda-forge
cuda-cudart-dev_linux-aarch64         13.0.96          h8f3c8d4_0                         conda-forge
cuda-cudart-static                    13.0.96          h8f3c8d4_0                         conda-forge
cuda-cudart-static_linux-aarch64      13.0.96          h8f3c8d4_0                         conda-forge
cuda-cudart_linux-aarch64             13.0.96          h8f3c8d4_0                         conda-forge
cuda-nvcc-dev_linux-aarch64           13.0.88          h4310d6a_0                         conda-forge
cuda-nvcc-impl                        13.0.88          h614329b_0                         conda-forge
cuda-nvcc-tools                       13.0.88          h614329b_0                         conda-forge
cuda-nvrtc                            13.0.88          h8f3c8d4_0                         conda-forge
cuda-nvvm-dev_linux-aarch64           13.0.88          h579c4fd_0                         conda-forge
cuda-nvvm-impl                        13.0.88          h7b14b0b_0                         conda-forge
cuda-nvvm-tools                       13.0.88          h7b14b0b_0                         conda-forge
cuda-pathfinder                       1.5.5            pyhc364b38_0                       conda-forge
cuda-python                           13.3.0           pyhcf101f3_2                       conda-forge
cuda-sanitizer-api                    13.0.85          h299c5c6_0                         conda-forge
cuda-version                          13.0             hc7b4dd1_3                         conda-forge
cudf                                  26.06.01         cuda13_cp311_abi3_260603_77ced62c  rapidsai
cupy                                  14.1.1           py312h2f1266c_0                    conda-forge
cupy-core                             14.1.1           py312h372fd59_0                    conda-forge
dlpack                                0.8              h2f0025b_3                         conda-forge
fsspec                                2026.6.0         pyhd8ed1ab_0                       conda-forge
gflags                                2.2.2            h5ad3122_1005                      conda-forge
glog                                  0.7.1            h468a4a4_0                         conda-forge
icu                                   78.3             hcab7f73_0                         conda-forge
keyutils                              1.6.3            h86ecc28_0                         conda-forge
krb5                                  1.22.2           h2fb54aa_1                         conda-forge
ld_impl_linux-aarch64                 2.45.1           default_h1979696_102               conda-forge
libabseil                             20260107.1       cxx17_h6983b43_0                   conda-forge
libarrow                              24.0.0           hedf04be_9_cuda                    conda-forge
libarrow-acero                        24.0.0           hb326ee9_9_cuda                    conda-forge
libarrow-compute                      24.0.0           hdd99842_9_cuda                    conda-forge
libarrow-dataset                      24.0.0           hb326ee9_9_cuda                    conda-forge
libarrow-substrait                    24.0.0           hf29bd21_9_cuda                    conda-forge
libblas                               3.11.0           8_haddc8a3_openblas                conda-forge
libbrotlicommon                       1.2.0            he30d5cf_1                         conda-forge
libbrotlidec                          1.2.0            he30d5cf_1                         conda-forge
libbrotlienc                          1.2.0            he30d5cf_1                         conda-forge
libcap                                2.78             hf9559e3_0                         conda-forge
libcblas                              3.11.0           8_hd72aa62_openblas                conda-forge
libcrc32c                             1.1.2            h01db608_0                         conda-forge
libcublas                             13.1.1.3         he38c790_0                         conda-forge
libcudf                               26.06.01         cuda13_260603_77ced62c             rapidsai
libcufft                              12.0.0.61        h8f3c8d4_0                         conda-forge
libcufile                             1.15.1.6         had8bf56_0                         conda-forge
libcufile-dev                         1.15.1.6         he38c790_0                         conda-forge
libcurand                             10.4.0.35        he38c790_1                         conda-forge
libcurl                               8.20.0           hc57f145_0                         conda-forge
libcusolver                           12.0.4.66        he38c790_1                         conda-forge
libcusparse                           12.6.3.3         h8f3c8d4_0                         conda-forge
libedit                               3.1.20250104     pl5321h976ea20_0                   conda-forge
libev                                 4.33             h31becfc_2                         conda-forge
libevent                              2.1.12           h4ba1bb4_1                         conda-forge
libexpat                              2.8.1            hfae3067_1                         conda-forge
libffi                                3.5.2            h376a255_0                         conda-forge
libgcc                                15.2.0           h8acb6b2_19                        conda-forge
libgcc-ng                             15.2.0           he9431aa_19                        conda-forge
libgfortran                           15.2.0           he9431aa_19                        conda-forge
libgfortran5                          15.2.0           h1b7bec0_19                        conda-forge
libgomp                               15.2.0           h8acb6b2_19                        conda-forge
libgoogle-cloud                       3.6.0            h235f271_0                         conda-forge
libgoogle-cloud-storage               3.6.0            h66d5b86_0                         conda-forge
libgrpc                               1.78.1           heab1e18_0                         conda-forge
libiconv                              1.18             h90929bb_2                         conda-forge
libkvikio                             26.06.00         cuda13_260603_5eb6c5d8             rapidsai
liblapack                             3.11.0           8_h88aeb00_openblas                conda-forge
liblzma                               5.8.3            he30d5cf_0                         conda-forge
libnghttp2                            1.68.1           hd3077d7_0                         conda-forge
libnl                                 3.11.0           h86ecc28_0                         conda-forge
libnsl                                2.0.1            h86ecc28_1                         conda-forge
libnuma                               2.0.18           he30d5cf_3                         conda-forge
libnvcomp                             5.2.0.10         he387df4_0                         conda-forge
libnvcomp-dev                         5.2.0.10         he387df4_0                         conda-forge
libnvfatbin                           13.0.85          h8f3c8d4_0                         conda-forge
libnvjitlink                          13.3.33          h8f3c8d4_0                         conda-forge
libnvptxcompiler-dev                  13.0.88          h579c4fd_0                         conda-forge
libnvptxcompiler-dev_linux-aarch64    13.0.88          h579c4fd_0                         conda-forge
libopenblas                           0.3.33           pthreads_h9d3fd7e_0                conda-forge
libopentelemetry-cpp                  1.27.0           hd82aec3_0                         conda-forge
libopentelemetry-cpp-headers          1.27.0           h8af1aa0_0                         conda-forge
libparquet                            24.0.0           h87079af_9_cuda                    conda-forge
libprotobuf                           6.33.5           h306233d_1                         conda-forge
libre2-11                             2025.11.05       hc5e897d_1                         conda-forge
librmm                                26.06.00         cuda13_260603_87184183             rapidsai
libsqlite                             3.53.2           h10b116e_0                         conda-forge
libssh2                               1.11.1           h18c354c_0                         conda-forge
libstdcxx                             15.2.0           hef695bb_19                        conda-forge
libstdcxx-ng                          15.2.0           hdbbeba8_19                        conda-forge
libsystemd0                           261              hb290c7d_0                         conda-forge
libthrift                             0.22.0           ha522d1d_2                         conda-forge
libudev1                              261              hb290c7d_0                         conda-forge
libutf8proc                           2.11.3           hec6f9f7_0                         conda-forge
libuuid                               2.42.2           h1022ec0_0                         conda-forge
libxcrypt                             4.4.36           h31becfc_1                         conda-forge
libxml2                               2.15.3           h869d058_0                         conda-forge
libxml2-16                            2.15.3           h79dcc73_0                         conda-forge
libzlib                               1.3.2            hdc9db2a_2                         conda-forge
llvmlite                              0.46.0           py312h7e1a490_0                    conda-forge
lz4-c                                 1.10.0           h5ad3122_1                         conda-forge
markdown-it-py                        4.2.0            pyhd8ed1ab_0                       conda-forge
mdurl                                 0.1.2            pyhd8ed1ab_1                       conda-forge
ncurses                               6.6              hf8d1292_0                         conda-forge
nlohmann_json                         3.12.0           h7ac5ae9_1                         conda-forge
numba                                 0.64.0           py312heba07a5_0                    conda-forge
numba-cuda                            0.28.2           py312h62ce522_0                    conda-forge
numpy                                 2.4.6            py312hce9e0af_0                    conda-forge
nvtx                                  0.2.15           py312hefbd42c_0                    conda-forge
openssl                               3.6.3            h546c87b_0                         conda-forge
orc                                   2.3.0            hce1ac79_0                         conda-forge
packaging                             26.2             pyhc364b38_0                       conda-forge
pandas                                2.3.3            py312hdc0efb6_1                    conda-forge
pip                                   26.1.2           pyh8b19718_0                       conda-forge
prometheus-cpp                        1.3.0            h7938499_0                         conda-forge
pyarrow                               24.0.0           py312h8025657_0                    conda-forge
pyarrow-core                          24.0.0           py312h4181037_0_cuda               conda-forge
pygments                              2.20.0           pyhd8ed1ab_0                       conda-forge
pylibcudf                             26.06.01         cuda13_cp311_abi3_260603_77ced62c  rapidsai
python                                3.12.13          h91f4b29_0_cpython                 conda-forge
python-dateutil                       2.9.0.post0      pyhe01879c_2                       conda-forge
python-gil                            3.12.13          hd8ed1ab_0                         conda-forge
python-tzdata                         2026.2           pyhd8ed1ab_0                       conda-forge
python_abi                            3.12             8_cp312                            conda-forge
pytz                                  2026.2           pyhcf101f3_0                       conda-forge
rapids-logger                         0.2.3            h4f43097_0                         rapidsai
rdma-core                             63.0             h1f0f388_1                         conda-forge
re2                                   2025.11.05       he0da282_1                         conda-forge
readline                              8.3              hb682ff5_0                         conda-forge
rich                                  15.0.0           pyhcf101f3_0                       conda-forge
rmm                                   26.06.00         cuda13_cp311_abi3_260603_87184183  rapidsai
s2n                                   1.7.4            h5288e76_1                         conda-forge
setuptools                            82.0.1           pyh332efcf_0                       conda-forge
six                                   1.17.0           pyhe01879c_1                       conda-forge
snappy                                1.2.2            he774c54_1                         conda-forge
tk                                    8.6.13           noxft_h0dc03b3_103                 conda-forge
typing_extensions                     4.15.0           pyhcf101f3_0                       conda-forge
tzdata                                2025c            hc9c84f9_1                         conda-forge
wheel                                 0.47.0           pyhd8ed1ab_0                       conda-forge
zlib                                  1.3.2            hdc9db2a_2                         conda-forge
zstd                                  1.5.7            h85ac4a6_6                         conda-forge

## Disk
Filesystem      Size  Used Avail Use% Mounted on
tmpfs            13G  2.2M   13G   1% /run
efivarfs        256K   20K  237K   8% /sys/firmware/efi/efivars
/dev/nvme0n1p2  3.7T   44G  3.5T   2% /
tmpfs            61G     0   61G   0% /dev/shm
tmpfs           5.0M  8.0K  5.0M   1% /run/lock
/dev/nvme0n1p1  298M  6.4M  292M   3% /boot/efi
tmpfs            13G  108K   13G   1% /run/user/126
tmpfs            13G   92K   13G   1% /run/user/1000

## Memory
               total        used        free      shared  buff/cache   available
Mem:           121Gi       3.0Gi       111Gi        12Mi       8.4Gi       118Gi
Swap:           15Gi          0B        15Gi
