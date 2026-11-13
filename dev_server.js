// Local preview: node dev_server.js  -> http://localhost:8787 (static site + /api with an in-memory store, password "dev")
const http=require("http"),fs=require("fs"),path=require("path");
process.env.SITE_PASSWORD="dev";
const mem={};
// sample numbers so the Stats page can be previewed without YouTube (clearly fake, dev only)
mem["ttm:stats"]={updated:new Date().toISOString(),channel:{subs:312,views:18450,videos:3},analytics:true,analytics_note:null,
 ypp:{targets:{watch_hours_now:4000,watch_hours_feb_2027:8000,shorts_views_90d_now:1e7,shorts_views_90d_feb_2027:2e7,subs:1000},long_watch_hours_365:212.4,shorts_views_90:15300},
 videos:[{id:"zaPe7_3Wbd4",title:"Hardik vs Arshdeep",slug:"hardik_arshdeep",format:"news",kind:"long",privacy:"public",published:"2026-11-02T10:00:00Z",views:900,likes:40,avg_view_pct:41,avg_view_s:210,subs_gained:6},
  {id:"yO-XGUHNPYU",title:"Kohli 2000 v NZ",slug:"kohli_2000_nz",format:"news",kind:"short",privacy:"public",published:"2026-11-05T10:00:00Z",views:12000,likes:600,avg_view_pct:78,avg_view_s:31,subs_gained:90}],
 formats:[{format:"news",kind:"short",videos:1,views:12000,avg_views:12000,avg_view_pct:78,watch_hours:103},{format:"news",kind:"long",videos:2,views:1500,avg_views:750,avg_view_pct:41,watch_hours:109}],
 history:[{date:"2026-11-01",subs:250,views:9000,long_watch_hours_365:150,shorts_views_90:5000},{date:"2026-11-13",subs:312,views:18450,long_watch_hours_365:212.4,shorts_views_90:15300}]};
const lib=require("./api/_lib");
lib.getJSON=async k=>mem[k]||null; lib.setJSON=async(k,v)=>{mem[k]=v}; lib.storageReady=()=>true;
const H={schedule:require("./api/schedule"),stats:require("./api/stats")};
const types={".html":"text/html",".json":"application/json",".png":"image/png",".webp":"image/webp",".js":"text/javascript"};
http.createServer(async(req,res)=>{
  const u=new URL(req.url,"http://x");
  if(u.pathname.startsWith("/api/")){
    const h=H[u.pathname.slice(5)]; if(!h){res.statusCode=404;return res.end("{}")}
    let b="";for await(const c of req)b+=c;
    req.query=Object.fromEntries(u.searchParams); req.body=b?JSON.parse(b):undefined;
    res.status=c=>{res.statusCode=c;return res}; res.json=o=>{res.setHeader("content-type","application/json");res.end(JSON.stringify(o))};
    return h(req,res);
  }
  let p=path.join("site",u.pathname==="/"?"index.html":u.pathname);
  fs.readFile(p,(e,d)=>{if(e){res.statusCode=404;return res.end("nf")}res.setHeader("content-type",types[path.extname(p)]||"application/octet-stream");res.end(d)});
}).listen(8787,()=>console.log("http://localhost:8787"));
