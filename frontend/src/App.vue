<template>
  <div class="container">
    <el-card class="title-card">
      <h1>小说合并工具</h1>
    </el-card>

    <el-row :gutter="20" class="settings-row">
      <el-col :span="form.generateCover ? 8 : 0">
        <el-card class="cover-card" :class="{ 'is-dragging': isCoverDragging }"
          v-show="form.generateCover"
          @dragenter="handleCoverDragEnter"
          @dragover="handleCoverDragOver"
          @dragleave="handleCoverDragLeave"
          @drop="handleCoverDrop"
        >
          <template #header>
            <div class="card-header">
              <span>上传封面图片</span>
              <el-button size="small" @click="handleCoverUpload">选择图片</el-button>
              <input
                ref="coverImageRef"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleCoverChange"
              />
            </div>
          </template>

          <div v-if="coverImage" class="cover-preview">
            <img :src="coverImage" alt="封面预览" />
            <el-button type="danger" size="small" circle @click="removeCover">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-empty v-else description="点击或拖拽上传封面图片（可选）" />
        </el-card>
      </el-col>

      <el-col :span="form.generateCover ? 16 : 24">
        <el-card class="header-card">
          <el-form :model="form" label-width="80px">
            <el-form-item label="书名">
              <el-input v-model="form.bookTitle" placeholder="请输入小说书名" />
            </el-form-item>
            <el-form-item label="作者">
              <el-input v-model="form.author" placeholder="请输入作者名" />
            </el-form-item>
            <el-form-item label="简介">
              <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入小说简介（可选）" />
            </el-form-item>
            <el-form-item label="生成封面">
              <el-switch v-model="form.generateCover" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

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
const coverImageRef = ref(null)
const coverImage = ref(null)
const coverImageFile = ref(null)
const isCoverDragging = ref(false)
const previewVisible = ref(false)
const previewContent = ref('')
const previewLoading = ref(false)
const mergeLoading = ref(false)

const form = reactive({
  bookTitle: '',
  author: '',
  description: '',
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

const handleCoverUpload = () => {
  coverImageRef.value.click()
}

const handleCoverChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    processCoverFile(file)
  }
  event.target.value = ''
}

const handleCoverDragEnter = (e) => {
  e.preventDefault()
  isCoverDragging.value = true
}

const handleCoverDragOver = (e) => {
  e.preventDefault()
}

const handleCoverDragLeave = (e) => {
  e.preventDefault()
  if (!e.currentTarget.contains(e.relatedTarget)) {
    isCoverDragging.value = false
  }
}

const handleCoverDrop = (e) => {
  e.preventDefault()
  isCoverDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processCoverFile(file)
  } else {
    ElMessage.warning('请上传图片文件')
  }
}

const processCoverFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    coverImage.value = e.target.result
    coverImageFile.value = file
  }
  reader.readAsDataURL(file)
}

const removeCover = () => {
  coverImage.value = null
  coverImageFile.value = null
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
  formData.append('description', form.description || '')
  formData.append('generate_cover', form.generateCover)
  
  if (coverImageFile.value) {
    formData.append('cover_image', coverImageFile.value)
  }
  
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
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.title-card {
  margin-bottom: 20px;
  text-align: center;
}

.title-card h1 {
  margin: 0;
  font-size: 24px;
}

.settings-row {
  margin-bottom: 20px;
}

.settings-row .el-col {
  display: flex;
  flex-direction: column;
}

.header-card {
  height: 100%;
  width: 100%;
}

.cover-card {
  height: 100%;
  width: 100%;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-card.is-dragging {
  border: 2px dashed #409eff;
  background-color: #ecf5ff;
}

.cover-card.is-dragging {
  border: 2px dashed #409eff;
  background-color: #ecf5ff;
}

.cover-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  flex: 1;
}

.cover-preview img {
  max-width: 160px;
  max-height: 220px;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.cover-preview .el-button {
  position: absolute;
  top: -10px;
  right: calc(50% - 90px);
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
