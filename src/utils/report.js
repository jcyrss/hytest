var FOLDER_ALL_CASES = false //是否为精简模式的标记
var ERROR_INFOS = [];  // 错误信息列表
var current_error_idx = -1;

// 页面加载后执行的函数
window.addEventListener("load", function(){
    // 所有 .folder_header 添加点击事件处理
    let folderHeaderEles = document.querySelectorAll(".folder_header");
    folderHeaderEles.forEach(function(ele) {
        ele.addEventListener("click", function(event) {
        let fb = event.target.closest('.folder_header').nextElementSibling;
        fb.style.display = fb.style.display === 'none' ? 'block' : 'none'
        });
    });

    // 找到所有的错误信息对象
    ERROR_INFOS = document.querySelectorAll(".error-info");
});



function toggle_folder_all_cases(){
    let eles = document.querySelectorAll(".folder_body");
    
    FOLDER_ALL_CASES = !FOLDER_ALL_CASES;
    document.getElementById('display_mode').innerHTML = FOLDER_ALL_CASES? "详细" : "精简"

    for (const ele of eles){
        ele.style.display =  FOLDER_ALL_CASES? "none": "block"
    }
    
}



function previous_error(){
    // 查找错误必须是详细模式
    if (FOLDER_ALL_CASES)
        toggle_folder_all_cases()

    current_error_idx -= 1; 
    if (current_error_idx<0)
        current_error_idx = 0

    
    let error = ERROR_INFOS[current_error_idx];

    error.scrollIntoView({behavior: "smooth", block: "center", inline: "start"});

    
}


function next_error(){
    
    // 查找错误必须是详细模式
    if (FOLDER_ALL_CASES)
        toggle_folder_all_cases()

    current_error_idx += 1;
    if (current_error_idx > ERROR_INFOS.length-1)
        current_error_idx = ERROR_INFOS.length-1

    let error = ERROR_INFOS[current_error_idx];

    error.scrollIntoView({behavior: "smooth", block: "center", inline: "start"});
    
}