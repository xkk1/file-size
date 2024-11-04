/*
This file is part of file-size.
Copyright (C) 2024  xkk1

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/
// 文件大小
"use strict";
// IEC KiB    1024 B = 1 KiB
// 二进制词头 https://zh.wikipedia.org/wiki/%E4%BA%8C%E9%80%B2%E4%BD%8D%E5%89%8D%E7%BD%AE%E8%A9%9E
// IEC 60027-2 https://zh.wikipedia.org/wiki/IEC_60027-2
let binary_prefix = "KMGTPEZYRQ";  // TiB, GiB, MiB, KiB
// SI kB    1000 B = 1 kB
// 国际单位制词头 https://zh.wikipedia.org/wiki/%E5%9B%BD%E9%99%85%E5%8D%95%E4%BD%8D%E5%88%B6%E8%AF%8D%E5%A4%B4
// 十进制前缀 SI https://zh.wikipedia.org/wiki/%E5%9B%BD%E9%99%85%E5%8D%95%E4%BD%8D%E5%88%B6
let metric_prefix = "kMGTPEZYRQ";  // TB, GB, MB, kB
let metric_prefix_zh = "千兆吉太拍艾泽尧容昆";
// JEDEC KB    1024 B = 1 KB
// JEDEC https://en.wikipedia.org/wiki/JEDEC_memory_standards
let jedec_prefix = binary_prefix;  // TB, GB, MB, KB

// 自动词缀
let auto_prefix = ["IEC 自动", "SI 自动", "JEDEC 自动", "SI 中文自动"];
// 所有支持的词缀
let all_prefix = ["B", "b"];
["B", "b"].forEach(b => {
    // IEC KiB    1024 B = 1 KiB
    for (let i = 0; i < binary_prefix.length; i++) {
        all_prefix.push(`IEC ${binary_prefix[i]}i${b}`);
    }
    // SI kB    1000 B = 1 kB
    for (let i = 0; i < metric_prefix.length; i++) {
        all_prefix.push(`SI ${metric_prefix[i]}${b}`);
    }
    // JEDEC KB    1024 B = 1 KB
    for (let i = 0; i < jedec_prefix.length; i++) {
        all_prefix.push(`JEDEC ${jedec_prefix[i]}${b}`);
    }
});
// SI 千字节    1000 字节 = 1 千字节
for (let i = 0; i < metric_prefix_zh.length; i++) {
    all_prefix.push(`SI ${metric_prefix_zh[i]}字节`);
    all_prefix.push(`SI ${metric_prefix_zh[i]}比特`);
}

// 上传文件列表
let fileList = [];

/**
 * 文件大小词缀转换为字节
 * @param {string} prefix 词缀 "B" "kB" "KiB"
 * @param {number} size 词缀大小，默认为1
 * @returns {number} 字节大小，未知词缀返回 -1
 */
function prefixToByte(prefix, size=1) {
    // prefix 不是字符或 size 不是数字，返回 0
    if (typeof prefix !== "string" || typeof size !== "number") return -1;
    if (prefix === "B" || prefix === "字节") return size;
    if (prefix === "b" || prefix === "比特") return size / 8;
    // IEC KiB    1024 B = 1 KiB
    for (let i = 0; i< binary_prefix.length; i++) {
        if (prefix === `${binary_prefix[i]}iB` || prefix === `IEC ${binary_prefix[i]}iB`) {
            return Math.pow(1024, i+1) * size;
        } else if (prefix === `${binary_prefix[i]}ib` || prefix === `IEC ${binary_prefix[i]}ib`) {
            return Math.pow(1024, i+1) * size / 8;
        }
    }
    // SI kB    1000 B = 1 kB
    for (let i = 0; i< metric_prefix.length; i++) {
        if (prefix === `${metric_prefix[i]}B` || prefix === `SI ${metric_prefix[i]}B`) {
            return Math.pow(1000, i+1) * size;
        } else if (prefix === `${metric_prefix[i]}b` || prefix === `SI ${metric_prefix[i]}b`) {
            return Math.pow(1000, i+1) * size / 8;
        }
    }
    // SI 千字节    1000 字节 = 1 千字节
    for (let i = 0; i< metric_prefix_zh.length; i++) {
        if (prefix === `${metric_prefix_zh[i]}字节` || prefix === `SI ${metric_prefix_zh[i]}字节`) {
            return Math.pow(1000, i+1) * size;
        } else if (prefix === `${metric_prefix_zh[i]}比特` || prefix === `SI ${metric_prefix_zh[i]}比特`) {
            return Math.pow(1000, i+1) * size / 8;
        }
    }
    // JEDEC KB    1024 B = 1 KB
    if (prefix === "KB") return Math.pow(1024, 1) * size;
    if (prefix === "Kb") return Math.pow(1024, 1) * size / 8;
    for (let i = 0; i< jedec_prefix.length; i++) {
        if (prefix === `JEDEC ${jedec_prefix[i]}B`) {
            return Math.pow(1024, i+1) * size;
        } else if (prefix === `JEDEC ${jedec_prefix[i]}b`) {
            return Math.pow(1024, i+1) * size / 8;
        }
    }
    return -2;
}

/**
 * 字节转换为包含词缀的文件大小
 * @param {number} byte 字节大小
 * @param {string} prefix 词缀 "B" "kB" "KiB"
 * @param {number} digits 保留小数位数
 * @returns {string} 文件大小 "1 B"
 */
function byteToPrefix(byte=1, prefix="B", digits=null) {
    if (digits !== null && (typeof digits !== "number" || digits < 0)) digits = null;
    /**
     * 自动选择词缀
     * @param {number} byte 字节大小
     * @param {string} prefixType "IEC"," SI", "JEDEC", "SI 中文"]
     * @param {string} basePrefix binary_prefix / metric_prefix / jedec_prefix
     * @param {number} base 1024 或 1000
     */
    function getAutoPrefix(byte, prefixType, basePrefix, base=1024) {
        let i = 0;
        while (byte >= base && i < basePrefix.length) {
            byte /= base;
            i++;
        }
        let b= "B";
        if (prefixType === "IEC") {
            if (i !== 0) {
                b = "iB";
            }
        }else if (prefixType === "SI 中文") {
            b = "字节";
            prefixType = "SI"
        }
        return `${(i === 0) ? '' : prefixType + ' ' + basePrefix[i-1]}${b}`;
    }
    if (prefix === "IEC 自动") {
        prefix = getAutoPrefix(byte, "IEC", binary_prefix, 1024);
    } else if (prefix === "SI 自动") {
        prefix = getAutoPrefix(byte, "SI", metric_prefix, 1000);
    } else if (prefix === "JEDEC 自动") {
        prefix = getAutoPrefix(byte, "JEDEC", jedec_prefix, 1024);
    } else if (prefix === "SI 中文自动") {
        prefix = getAutoPrefix(byte, "SI 中文", metric_prefix_zh, 1024);
    }
    let prefixByte = prefixToByte(prefix);
    if (prefixByte === -1) return "参数错误";
    if (prefixByte === -2) return "未知词缀";
    prefix = prefix.replace(/(SI|IEC|JEDEC) /, "");
    if (digits === null) return "" + (byte / prefixByte) + " " + prefix;
    return (byte / prefixByte).toFixed(digits) + " " + prefix;
}



/**
 * 初始化转换工具
 */
function initConversionTools() {
    // 初始化输入词缀选择框
    const inputPrefixSelectElement = document.getElementById('input-prefix');
    all_prefix.forEach(prefix => {
        const option = document.createElement("option");
        option.value = prefix;
        option.textContent = prefix;
        inputPrefixSelectElement.appendChild(option);
    });
    // inputPrefixSelectElement.selectedIndex = 14;
    // 初始化输出词缀选择框
    const outPrefixSelectElement = document.getElementById('output-prefix');
    auto_prefix.concat(all_prefix).forEach(prefix => {
        const option = document.createElement("option");
        option.value = prefix;
        option.textContent = prefix;
        outPrefixSelectElement.appendChild(option);
    });
    // outPrefixSelectElement.selectedIndex = 0;
    // 监听输入框变化
    const inputSizeInputElement = document.getElementById('input-size');
    const conversionResultSpanElement = document.getElementById('conversion-result');
    /**
     * 更新转换结果
     */
    function updateConversionResult() {
        let inputPrefix = inputPrefixSelectElement.value;
        let outPrefix = outPrefixSelectElement.value;
        let byte = prefixToByte(inputPrefix, Number(inputSizeInputElement.value));
        
        conversionResultSpanElement.textContent = 
            inputPrefix.replace(/^(SI|IEC|JEDEC) /, "") + 
            " = " + byteToPrefix(byte, outPrefix);
    }
    inputSizeInputElement.addEventListener("input", updateConversionResult);
    inputPrefixSelectElement.addEventListener("change", updateConversionResult);
    outPrefixSelectElement.addEventListener("change", updateConversionResult);
    // inputSizeInputElement.value = "1000";
    updateConversionResult();

}

/**
 * 更新显示文件列表
 */
function updateFileList() {
    const uploadPrefixSelectElement = document.getElementById('upload-prefix');
    let uploadResultElement = document.getElementById("upload-result");
    uploadResultElement.innerHTML = "";
    for (let i = fileList.length - 1; i >= 0; i--) {
        const file = fileList[i];
        console.log(file);
        const fileSpanElement = document.createElement("span");
        fileSpanElement.textContent = file.webkitRelativePath ? file.webkitRelativePath : file.name + " - " + byteToPrefix(file.size, uploadPrefixSelectElement.value);
        const fileElement = document.createElement("div");
        fileElement.appendChild(fileSpanElement);
        uploadResultElement.appendChild(fileElement);
    }
}

/**
 * 添加文件到文件列表并显示
 * @param {File[]} files 文件列表
 */
function addFiles(files) {
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        fileList.push(file);
    }
    updateFileList();
}

/**
 * 初始化拖放选择文件
 */
function initDragDrop() {
    // 使用拖放来选择文件 https://developer.mozilla.org/zh-CN/docs/Web/API/File_API/Using_files_from_web_applications#%E4%BD%BF%E7%94%A8%E6%8B%96%E6%94%BE%E6%9D%A5%E9%80%89%E6%8B%A9%E6%96%87%E4%BB%B6
    function dragenter(e) {
        e.stopPropagation();
        e.preventDefault();
        console.log("dragenter");
    }

    function dragover(e) {
        e.stopPropagation();
        e.preventDefault();
        console.log("dragover");
    }

    function drop(e) {
        e.stopPropagation();
        e.preventDefault();

        const dt = e.dataTransfer;
        const files = dt.files;

        addFiles(files);
        console.log(files);

    }

    const dropbox = document.getElementById("dropbox");
    dropbox.addEventListener("dragenter", dragenter, false);
    dropbox.addEventListener("dragover", dragover, false);
    dropbox.addEventListener("drop", drop, false);
}

/**
 * 初始化上传检测文件大小
 */
function initUpload() {
    // 初始化上传词缀选择框
    const uploadPrefixSelectElement = document.getElementById('upload-prefix');
    auto_prefix.concat(all_prefix).forEach(prefix => {
        const option = document.createElement("option");
        option.value = prefix;
        option.textContent = prefix;
        uploadPrefixSelectElement.appendChild(option);
    });
    // 清空列表按钮
    const clearButtonElement = document.getElementById("clear-button");
    clearButtonElement.addEventListener("click", () => {
        fileList = [];
        updateFileList();
    });
    uploadPrefixSelectElement.addEventListener("change", () => {
        updateFileList();
    });
    // 上传多文件
    const fileInputElement = document.getElementById("file-input");
    fileInputElement.addEventListener("change", () => {
        addFiles(fileInputElement.files);
    });
    // 上传目录
    const directoryInput = document.getElementById("directory-input");
    directoryInput.addEventListener("change", () => {
        addFiles(directoryInput.files);
    });
    // 使用拖放来选择文件
    initDragDrop();

}

document.addEventListener('DOMContentLoaded', function() {
    // 初始化转换工具
    initConversionTools();
    // 初始化上传检测文件大小
    initUpload();
});