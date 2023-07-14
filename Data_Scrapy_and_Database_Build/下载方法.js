// Chrome打开https://terms.naer.edu.tw/search/，直接在终端运行下列代码
// 下面这个1~100依次增大，直到1901~2000，2001~2027
// 要允许Download multiple files，会在下载文件夹下下载2027个文件


for(let i = 1; i <= 100; i++) {
    fetch(`https://terms.naer.edu.tw/refine-search/?page=${i}&page_size=1000&cache=1689019484135`, {
        "headers": {
            "accept": "*/*",
            "accept-language": "en;q=0.6",
            "sec-ch-ua": `"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"`,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": `"Windows"`,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "x-requested-with": "XMLHttpRequest"
        },
        "referrer": "https://terms.naer.edu.tw/",
        "referrerPolicy": "origin",
        "body": null,
        "method": "GET",
        "mode": "cors",
        "credentials": "include"
    }).then(response => response.text())
        .then(data => {
            const blob = new Blob([data], {type: 'text/html'});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `page_${i}.html`;
            link.click();
        });
}