<template>

  <div>
    <img alt="Vue logo" src="../assets/1_top.jpg">
<hr >

    <div class="st">
    <p>cp value:{{cp}}</p>
    <p>ppi value:{{ppi}}</p>
    </div>
    <hr >
    <div class="st">
    <p><b>Identification Result Num: </b></p>
        <table   v-for="(item, index) of tp" :key="index">
            <td>{{index}}:{{item}}</td>
        </table>
    <p><b>Identification Result Probability:</b> </p>
        <table  v-for="(item, index) of nameArr" :key="index">
            <td>{{item.name}}:{{item.prob}}%</td>
        </table>
    <hr >
    </div>
    <el-upload
    v-loading="showLoading"
    :action="uploadAPI"
    :multiple="true"
    :auto-upload="true"
    list-type="picture-card"
    :on-success="on_progress"
    >
    <div>upload_and_submit</div><!-- 改名字-->
    <!--  asdasda -->
    </el-upload>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  },
  data(){
    return {
      uploadAPI: 'http://127.0.0.1:5000/upload', //等域名来了再改
      showLoading: false,
      nameObj:{},
      nameArr:[],
      cp: 0,
      ppi: 0,
      feeding_type:{},
      tp:{},
      dialogImageUrl: '',
      dialogVisible: false
    }
  },
  methods: {
    on_progress(event,file,filelist){
      console.log(event,file,filelist)
      let {data} = event;
      console.log(data)
      file.url = 'http://127.0.0.1:5000'+data[1];
      console.log('上传成功的文件:', file);
      if(this.nameObj[data[0]]) this.nameObj[data[0]]++;
      else this.nameObj[data[0]]=1;
      let flag = true;
      for(let o of this.nameArr){
        if(o.name === data[0]) {
          o.count++;
          flag=false;
        }
      }
      if(flag) this.nameArr.push({name:data[0].class_name,prob:data[0].precentage*100,count:1})
      let num = this.nameArr.reduce((a,b)=>a+b.count,0);
      let sl = {
        'Acrobeles': {cp:2, ppi:0,feeding_type:'Bacteria'},
        'Acrobeloides': {cp:2, ppi:0,feeding_type:"Bacteria"},
        'Amplimerlinius':	{cp:0, ppi:3,feeding_type:'Plant'},
        'Aphelenchoides':	{cp:2, ppi:0,feeding_type:'Fungi'},
        'Aporcelaimus':	{cp:5, ppi:0,feeding_type:'Predator'},
        'Axonchium': 	{cp:5, ppi:0,feeding_type:'Omnivore'},
        'Discolaimus':{cp:5, ppi:0,feeding_type:'Omnivore'},
        'Ditylenchus':{cp:2, ppi:2,feeding_type:'Fungi'},
        'Dorylaimus':{cp:4, ppi:0,feeding_type:'Omnivore'},
        'Eudorylaimus':{cp:4, ppi:0,feeding_type:'Omnivore'},
        'Helicotylenchus': {cp:0, ppi:3,feeding_type:'Plant'},
        'Mesodorylaimus':{cp:4, ppi:0,feeding_type:'Omnivore'},
        'Miconchus':{cp:4, ppi:0,feeding_type:'Predator'},
        'Mylonchulus':{cp:4, ppi:0,feeding_type:'Predator'},
        'Panagrolaimus':{cp:1, ppi:0,feeding_type:'Bacteria'},
        'Pratylenchus': {cp:0, ppi:3,feeding_type:'Plant'},
        'Pristionchus':{cp:1, ppi:0,feeding_type:'Bacteria'},
        'Rhbiditis':{cp:1, ppi:0,feeding_type:'Bacteria'},
        'Xenocriconema':{cp:0, ppi:3,feeding_type:'Plant'},
      }
      this.cp=0;
      this.ppi=0;
      this.feeding_type={};
      this.tp={};
      this.nameArr.forEach(e=>{
        this.cp+=sl[e.name].cp*e.count/num;
        this.ppi+=sl[e.name].ppi*e.count/num;
      if(!this.tp[e.name]){
             this.tp[e.name]= 1;
        }else{
            this.tp[e.name]+= 1;
        }
      if(!this.feeding_type[sl[e.name].feeding_type]){
            this.feeding_type[sl[e.name].feeding_type] = 1;
        }else{
            this.feeding_type[sl[e.name].feeding_type] += 1;
        }
        // this.feeding_type.Bacteria+=sl[e.name].feeding_type;
      }
      );
      this.cp=this.cp.toFixed(3)
      this.ppi=this.ppi.toFixed(3)
      // let cp=2*count_9/len(a)+2*count_19/len(a)+2*count_11/len(a)+5*count_13/len(a)+5*count_12/len(a)+5*count_14/len(a)+2*count_1/len(a)+4*count_18/len(a)+4*count_15/len(a)+4*count_16+4*count_17/len(a)+4*count_5/len(a)+count_6+count_10+count_7
      // let ppi=3*count_2/len(a)+2*count_1/len(a)+3*count_3/len(a)+3*count_8/len(a)+3*count_4/len(a)
      // let name=[];
      // for(let i in nameObj){
      //   if(name[i]) name[i]++;
      //   else name[i]=1;
      // }
      // this.nameArr = name;
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.divcss5-left
{
    float:left;
    width:250px;
    height:50px;

}

h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.st {
    margin-left: 10px;
    text-align: left;
    width:70%;
    margin: 0 auto;
}
.st span{
  margin-left: 10px;
  text-align: left;
}

</style>
