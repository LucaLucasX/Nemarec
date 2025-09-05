module.exports = {
    publicPath: "/nemarec/", // 部署应⽤包时的基本 URL
    outputDir: "dist", // npm run build ⽣成的⽂件夹，默认是dist
    assetsDir: "static", // 在kaixin⽂件夹下⾯⽣成static⽬录存放js,img,css等静态资源
    indexPath: "index.html", // ⽣成的单⽂件的，⽂件名，
    devServer: {
        host:'0.0.0.0',
        disableHostCheck: true,
        proxy: {
            '/api': {
                target: '0.0.0.0:5000',//后端接口地址，按自己的改
                changeOrigin: true,//是否允许跨越
                pathRewrite: {
                    '^/api': ''
                }
            }
        }
    }
}
