var get_class_app = new Vue({
    el: '#get_class_app',
    data: {
        text: '',
        classifier_result: '',
        vActive: false,
        hActive: true,
        loading: false,
    },
  methods: {
    getClass: function () {
      const vm = this
      vm.loading = true
      console.log(vm.loading)
      axios.get('api/model/?text=' + this.text)
      .then(function(response){
      if (response.status == 200){
        console.log(response.status)
        vm.classifier_result = response.data
        vm.vActive = true
        vm.hActive = false
        vm.loading = false
      } else if (response.status == 204 || text == ''){
        vm.vActive = false
        vm.hActive = true
        alert('Получена ошибка 204: передано пустое поле с текстом')
      }
      })
    }
  }
})


var list_of_classes = new Vue({
    el: '#list_of_classes',
    data: {
        classes: [],
        checkedClass: 0,
    },
  created: function () {
    const vm = this
    axios.get('/api/texts/?format=json&method=getClasses')
    .then(function(response){
        vm.classes = response.data
        console.log(this.checkedClass)
      })
    },
  methods: {
    updateTable: function() {
      tableRender.created()
    }
  }
})


var tableRender = new Vue({
    el: '#tableRender',
    data: {
        goods: "",
        nextLink: "",
        prevLink: "",
        curPage: 1,
        count: 0,
  },
  methods: {
      created: function () {
        const vm = this
        if (list_of_classes.checkedClass == 0) {
            axios.get('/api/texts/?method=getAllTexts&page=' + this.curPage)
            .then(function(response){
                vm.nextLink = response.data.next
                vm.prevLink = response.data.previous
                vm.goods = response.data.results
                vm.count = response.data.count
            })
        } else {
                axios.get('/api/texts/?method=getAllTextsByClass&category=' + list_of_classes.checkedClass + '&page=' + this.curPage)
                .then(function(response){
                    vm.nextLink = response.data.next
                    vm.prevLink = response.data.previous
                    vm.goods = response.data.results
                    vm.count = response.data.count
                })
            }
      },
  },
  mounted() {
     this.created();
  },
  update() {
     this.created();
  }
})

var curPage = new Vue({
    el: '#curPage',
    data: tableRender,
    methods:{
        nextPage: function() {
            if (this.nextLink != null){
                this.curPage += 1
                console.log("Page = " + this.curPage)
                tableRender.created()
            }
        },
        prevPage: function() {
            if (this.prevLink != null){
                this.curPage -= 1
                console.log("Page = " + this.curPage)
                tableRender.created()
            }
        },
    }
})


