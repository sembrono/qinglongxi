const fs = require('fs');
const path = require('path');
const glob = require('glob');
const axios = require('axios');
const { exec } = require('child_process');

// === 配置 ===
// Telegram Bot token 和 用户ID，从环境变量中读取
const TG_BOT_TOKEN = process.env.TG_BOT_TOKEN;
const TG_USER_ID = process.env.TG_USER_ID;

if (!TG_BOT_TOKEN || !TG_USER_ID) {
  throw new Error("请在环境变量中设置 TG_BOT_TOKEN 和 TG_USER_ID");
}

// 基础URL富豪短剧API根地址
const BASE_URL = 'https://app.whhxtc.ltd';

// === 富豪短剧功能示范（简化版） ===
// 这里可将原富豪短剧JS中核心方法封装调用，为示范仅执行外部脚本演示
function runFuhaoScript(jsFilePath) {
  return new Promise((resolve, reject) => {
    console.log(`► 开始执行富豪短剧脚本: ${jsFilePath}`);
    exec(`node ${jsFilePath}`, {timeout: 10 * 60 * 1000}, (err, stdout, stderr) => {
      if (err) {
        console.error(`❌ 执行富豪短剧脚本出错: ${err}`);
        reject(err);
      } else {
        console.log(`► 富豪短剧脚本执行完成:\n${stdout}`);
        if(stderr) console.warn(`脚本执行警告:\n${stderr}`);
        resolve(true);
      }
    });
  });
}

// === 日志读取与 Telegram 推送 ===
async function pushToTG(scriptName, logTime, logContent) {
  const title = `【${scriptName}】_ ${logTime}`;
  const msg = `${title}\n\n${logContent}`;
  const url = `https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage`;
  try {
    const res = await axios.post(url, null, {
      params: {
        chat_id: TG_USER_ID,
        text: msg,
        parse_mode: "HTML"
      }
    });
    if(res.status === 200){
      console.log(`✅ TG推送成功: ${title}`);
    } else {
      console.error(`❌ TG推送失败，状态码: ${res.status}, 内容: ${res.data}`);
    }
  } catch(e) {
    console.error(`❌ TG推送异常: ${e.message}`);
  }
}

async function readLatestQLLog(taskNamePrefix, scriptName, contentLimit = 2000) {
  const logBaseDir = "/ql/data/log";
  if(!fs.existsSync(logBaseDir)){
    const err = "❌ 青龙日志根目录不存在：/ql/data/log";
    console.error(err);
    return err;
  }
  const taskDirs = glob.sync(path.join(logBaseDir, `${taskNamePrefix}*`));
  if(taskDirs.length === 0){
    const err = `❌ 未找到[${taskNamePrefix}]相关日志文件夹`;
    console.error(err);
    return err;
  }
  let latestTaskDir = taskDirs[0];
  let latestTime = fs.statSync(latestTaskDir).ctimeMs;
  for(const dir of taskDirs){
    const stat = fs.statSync(dir);
    if(stat.ctimeMs > latestTime){
      latestTaskDir = dir;
      latestTime = stat.ctimeMs;
    }
  }
  const allFiles = fs.readdirSync(latestTaskDir)
    .map(f => path.join(latestTaskDir, f))
    .filter(f => fs.statSync(f).isFile());
  if(allFiles.length === 0){
    const err = `❌ 文件夹[${latestTaskDir}]内无文件`;
    console.error(err);
    return err;
  }
  let latestLogFile = allFiles[0];
  let latestFileTime = fs.statSync(latestLogFile).ctimeMs;
  for(const file of allFiles){
    const stat = fs.statSync(file);
    if(stat.ctimeMs > latestFileTime){
      latestLogFile = file;
      latestFileTime = stat.ctimeMs;
    }
  }
  console.log(`✅ 正在读取文件：${latestLogFile}`);
  let logContent = '';
  try {
    logContent = fs.readFileSync(latestLogFile, {encoding: 'utf8'}).slice(0, contentLimit);
  } catch(e) {
    console.error(`❌ 读取日志文件失败: ${e.message}`);
  }
  const logTime = new Date(latestFileTime).toISOString().slice(0,16).replace('T',' ');
  await pushToTG(scriptName, logTime, logContent);
  return `✅ 内容读取完成\n📄 读取文件：${latestLogFile}\n📝 推送内容长度：${logContent.length}字符\n📱 已推送【${scriptName}_信息_${logTime}】到Telegram`;
}

// === 主流程 ===
(async () => {
  console.log("=".repeat(60));
  console.log("  富豪短剧自动执行及青龙日志推送合并脚本  ");
  console.log("=".repeat(60));

  const jsFile = "富豪短剧.js"; // 相对路径或绝对路径
  if (!fs.existsSync(jsFile)) {
    console.error(`❌ JS脚本文件 ${jsFile} 不存在，请确保路径正确`);
    process.exit(1);
  }
  try {
    await runFuhaoScript(jsFile);

    const currentScriptName = path.basename(jsFile, ".js");
    const logResult = await readLatestQLLog(currentScriptName, currentScriptName);

    console.log(logResult);
  } catch (error) {
    console.error(`❌ 执行发生错误: ${error}`);
  }

  console.log("=".repeat(60));
})();
