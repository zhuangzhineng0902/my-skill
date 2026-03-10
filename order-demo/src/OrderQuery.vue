<template>
  <div class="order-query-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">订单管理查询</h1>
      <p class="page-description">查询和管理所有订单信息</p>
    </div>

    <!-- 查询条件卡片 -->
    <el-card class="query-card" shadow="never">
      <el-form :model="queryParams" inline class="query-form">
        <el-form-item label="订单编号">
          <el-input
            v-model="queryParams.orderNo"
            placeholder="请输入订单编号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="queryParams.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        
        <el-form-item label="发起人">
          <el-input
            v-model="queryParams.initiator"
            placeholder="请输入发起人"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        
        <el-form-item label="金额范围">
          <el-input-number
            v-model="queryParams.minAmount"
            placeholder="最小金额"
            :min="0"
            :precision="2"
            :controls="false"
            style="width: 120px"
          />
          <span style="margin: 0 8px">-</span>
          <el-input-number
            v-model="queryParams.maxAmount"
            placeholder="最大金额"
            :min="0"
            :precision="2"
            :controls="false"
            style="width: 120px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格卡片 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">订单列表</span>
          <div class="card-actions">
            <el-button type="primary" size="small">
              <el-icon><Plus /></el-icon>
              新增订单
            </el-button>
            <el-button size="small">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
        :header-cell-style="{ background: '#F5F7FA', color: '#606266', fontWeight: 600 }"
      >
        <el-table-column prop="orderNo" label="订单编号" width="180" fixed>
          <template #default="{ row }">
            <el-link type="primary" @click="handleViewDetail(row)">
              {{ row.orderNo }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="createTime" label="创建时间" width="180">
          <template #default="{ row }">
            <span style="color: var(--color-text-secondary)">{{ row.createTime }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="initiator" label="发起人" width="120">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 8px">
              <el-avatar :size="24" :src="row.avatar">
                {{ row.initiator?.charAt(0) }}
              </el-avatar>
              <span>{{ row.initiator }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="amount" label="金额" width="140" align="right">
          <template #default="{ row }">
            <span style="font-weight: 600; color: var(--color-danger)">
              ¥{{ row.amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="color: var(--color-text-secondary)">{{ row.remark || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewDetail(row)">
              查看
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 查询参数
const queryParams = reactive({
  orderNo: '',
  dateRange: null,
  initiator: '',
  minAmount: null,
  maxAmount: null
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 模拟数据生成
const generateMockData = (count = 50) => {
  const statuses = ['待处理', '处理中', '已完成', '已取消']
  const names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
  
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    orderNo: `ORD${Date.now().toString().slice(-8)}${String(i + 1).padStart(4, '0')}`,
    createTime: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
      .toLocaleString('zh-CN', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }),
    initiator: names[Math.floor(Math.random() * names.length)],
    amount: Math.floor(Math.random() * 100000) + 100,
    status: statuses[Math.floor(Math.random() * statuses.length)],
    remark: Math.random() > 0.5 ? '备注信息' : ''
  }))
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    '待处理': 'warning',
    '处理中': 'info',
    '已完成': 'success',
    '已取消': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取表格数据
const fetchTableData = async () => {
  loading.value = true
  
  // 模拟API请求延迟
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 模拟数据
  const allData = generateMockData(100)
  
  // 筛选
  let filtered = allData
  if (queryParams.orderNo) {
    filtered = filtered.filter(item => 
      item.orderNo.toLowerCase().includes(queryParams.orderNo.toLowerCase())
    )
  }
  if (queryParams.initiator) {
    filtered = filtered.filter(item => 
      item.initiator.includes(queryParams.initiator)
    )
  }
  if (queryParams.minAmount !== null) {
    filtered = filtered.filter(item => item.amount >= queryParams.minAmount)
  }
  if (queryParams.maxAmount !== null) {
    filtered = filtered.filter(item => item.amount <= queryParams.maxAmount)
  }
  
  // 分页
  pagination.total = filtered.length
  const start = (pagination.current - 1) * pagination.pageSize
  tableData.value = filtered.slice(start, start + pagination.pageSize)
  
  loading.value = false
}

// 查询
const handleQuery = () => {
  pagination.current = 1
  fetchTableData()
}

// 重置
const handleReset = () => {
  Object.assign(queryParams, {
    orderNo: '',
    dateRange: null,
    initiator: '',
    minAmount: null,
    maxAmount: null
  })
  pagination.current = 1
  fetchTableData()
}

// 查看详情
const handleViewDetail = (row) => {
  ElMessage.info(`查看订单: ${row.orderNo}`)
}

// 编辑
const handleEdit = (row) => {
  ElMessage.info(`编辑订单: ${row.orderNo}`)
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除订单 ${row.orderNo} 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('删除成功')
    fetchTableData()
  }).catch(() => {})
}

// 分页变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchTableData()
}

const handleCurrentChange = (page) => {
  pagination.current = page
  fetchTableData()
}

// 初始化
onMounted(() => {
  fetchTableData()
})
</script>

<style scoped>
.order-query-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--space-8);
  min-height: 100vh;
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.page-description {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.query-card {
  margin-bottom: var(--space-6);
  border-radius: var(--radius-lg);
}

.query-card :deep(.el-card__body) {
  padding: var(--space-6);
}

.query-form {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.query-form :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

.query-form :deep(.el-form-item__label) {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.table-card {
  border-radius: var(--radius-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.card-actions {
  display: flex;
  gap: var(--space-2);
}

.table-card :deep(.el-card__header) {
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.table-card :deep(.el-card__body) {
  padding: var(--space-6);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border);
}

/* 响应式 */
@media (max-width: 768px) {
  .order-query-page {
    padding: var(--space-4);
  }
  
  .query-form {
    flex-direction: column;
  }
  
  .card-header {
    flex-direction: column;
    gap: var(--space-4);
    align-items: flex-start;
  }
}
</style>