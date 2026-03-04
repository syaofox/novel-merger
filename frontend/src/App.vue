<template>
  <div class="container">
    <el-card class="header-card">
      <template #header>
        <h1>小说合并工具</h1>
      </template>
      
      <el-form :model="form" label-width="100px">
        <el-form-item label="书名">
          <el-input v-model="form.bookTitle" placeholder="请输入小说书名" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="form.author" placeholder="请输入作者名" />
        </el-form-item>
        <el-form-item label="生成封面">
          <el-switch v-model="form.generateCover" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="upload-card" :class="{ 'is-dragging': isDragging }"
      @dragenter="handleDragEnter"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <template #header>
        <div class="card-header">
          <span>上传章节文件</span>
          <el-button type="primary" @click="handleUpload">选择文件</el-button>
          <input
            ref="fileInput"
            type="file"
            multiple
            accept=".txt,.md"
            style="display: none"
            @change="handleFileChange"
          />
        </div>
      </template>

      <el-empty v-if="fileList.length === 0" description="请上传TXT或Markdown文件" />
      
      <div v-else class="file-list">
        <draggable
          v-model="fileList"
          item-key="name"
          handle=".drag-handle"
          animation="200"
        >
          <template #item="{ element, index }">
            <div class="file-item">
              <el-icon class="drag-handle"><Rank /></el-icon>
              <span class="file-index">{{ index + 1 }}.</span>
              <span class="file-name">{{ element.name }}</span>
              <el-button
                type="danger"
                size="small"
                circle
                @click="removeFile(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </draggable>
      </div>
    </el-card>

    <div class="actions">
      <el-button type="info" @click="handlePreview" :loading="previewLoading">
        预览合并结果
      </el-button>
      <el-button type="success" @click="handleMerge" :loading="mergeLoading">
        生成EPUB
      </el-button>
    </div>

    <el-dialog v-model="previewVisible" title="预览" width="80%">
      <pre class="preview-content">{{ previewContent }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Rank, Delete } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import axios from 'axios'

const fileInput = ref(null)
const fileList = ref([])
const isDragging = ref(false)
const previewVisible = ref(false)
const previewContent = ref('')
const previewLoading = ref(false)
const mergeLoading = ref(false)

const form = reactive({
  bookTitle: '',
  author: '',
  generateCover: true
})

const handleUpload = () => {
  fileInput.value.click()
}

const handleFileChange = (event) => {
  const files = event.target.files
  for (const file of files) {
    const ext = file.name.split('.').pop().toLowerCase()
    if (ext === 'txt' || ext === 'md') {
      fileList.value.push({
        name: file.name,
        file: file
      })
    } else {
      ElMessage.warning(`不支持的文件格式: ${file.name}`)
    }
  }
  event.target.value = ''
}

const handleDragEnter = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragOver = (e) => {
  e.preventDefault()
}

const handleDragLeave = (e) => {
  e.preventDefault()
  if (!e.currentTarget.contains(e.relatedTarget)) {
    isDragging.value = false
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const files = e.dataTransfer.files
  for (const file of files) {
    const ext = file.name.split('.').pop().toLowerCase()
    if (ext === 'txt' || ext === 'md') {
      fileList.value.push({
        name: file.name,
        file: file
      })
    } else {
      ElMessage.warning(`不支持的文件格式: ${file.name}`)
    }
  }
}

const removeFile = (index) => {
  fileList.value.splice(index, 1)
}

const handlePreview = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }

  previewLoading.value = true
  const formData = new FormData()
  
  for (const item of fileList.value) {
    formData.append('files', item.file)
  }
  
  const order = fileList.value.map((_, i) => i).join(',')
  formData.append('order', order)

  try {
    const response = await axios.post('/api/preview', formData)
    previewContent.value = response.data.content
    previewVisible.value = true
  } catch (error) {
    ElMessage.error('预览失败: ' + error.message)
  } finally {
    previewLoading.value = false
  }
}

const handleMerge = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }

  if (!form.bookTitle) {
    ElMessage.warning('请输入书名')
    return
  }

  mergeLoading.value = true
  const formData = new FormData()
  
  for (const item of fileList.value) {
    formData.append('files', item.file)
  }
  
  formData.append('book_title', form.bookTitle)
  formData.append('author', form.author || '未知作者')
  formData.append('generate_cover', form.generateCover)
  
  const order = fileList.value.map((_, i) => i).join(',')
  formData.append('order', order)

  try {
    const response = await axios.post('/api/merge', formData, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${form.bookTitle}.epub`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('EPUB生成成功！')
  } catch (error) {
    ElMessage.error('生成失败: ' + error.message)
  } finally {
    mergeLoading.value = false
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-card.is-dragging {
  border: 2px dashed #409eff;
  background-color: #ecf5ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-list {
  max-height: 400px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
  gap: 10px;
}

.file-item:hover {
  background-color: #f5f7fa;
}

.drag-handle {
  cursor: move;
  color: #909399;
}

.file-index {
  color: #909399;
  min-width: 30px;
}

.file-name {
  flex: 1;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.preview-content {
  max-height: 500px;
  overflow-y: auto;
  white-space: pre-wrap;
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}
</style>
