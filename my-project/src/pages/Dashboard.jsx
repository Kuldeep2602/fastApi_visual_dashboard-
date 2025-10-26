import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  Trash2, 
  BarChart3, 
  FileText, 
  Loader2,
  AlertCircle,
  TrendingUp,
  Calendar
} from 'lucide-react';
import { getDatasets, deleteDataset, getDatasetData, getChartData } from '../services/dataService';
import DataTable from '../components/DataTable';
import ChartView from '../components/ChartView';

export default function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'chart'
  const [chartConfig, setChartConfig] = useState({
    type: 'bar',
    column: '',
    aggregation: 'count'
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDatasets();
  }, []);

  useEffect(() => {
    if (selectedDataset) {
      if (viewMode === 'table') {
        fetchTableData();
      } else {
        fetchChartData();
      }
    }
  }, [selectedDataset, currentPage, viewMode, chartConfig]);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await getDatasets();
      setDatasets(response.data);
      if (response.data.length > 0) {
        setSelectedDataset(response.data[0]);
      }
    } catch (err) {
      setError('Failed to load datasets');
    } finally {
      setLoading(false);
    }
  };

  const fetchTableData = async () => {
    if (!selectedDataset) return;

    try {
      const response = await getDatasetData(selectedDataset.id, {
        page: currentPage,
        page_size: 20
      });
      setTableData(response.data.data || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (err) {
      setError('Failed to load table data');
    }
  };

  const fetchChartData = async () => {
    if (!selectedDataset || !chartConfig.column) return;

    try {
      const response = await getChartData(
        selectedDataset.id,
        chartConfig.column,
        chartConfig.aggregation
      );
      setChartData(response.data);
    } catch (err) {
      setError('Failed to load chart data');
    }
  };

  const handleDeleteDataset = async (datasetId) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) {
      return;
    }

    try {
      await deleteDataset(datasetId);
      if (selectedDataset?.id === datasetId) {
        setSelectedDataset(null);
        setTableData([]);
        setChartData(null);
      }
      fetchDatasets();
    } catch (err) {
      setError('Failed to delete dataset');
    }
  };

  const getColumns = () => {
    if (tableData.length === 0) return [];
    return Object.keys(tableData[0]);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 dark:text-blue-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-300">Loading your datasets...</p>
        </div>
      </div>
    );
  }

  if (datasets.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-12">
            <div className="inline-flex p-4 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-6">
              <Database className="h-16 w-16 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              No Datasets Yet
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              Upload your first dataset to start visualizing and analyzing your data
            </p>
            <button
              onClick={() => navigate('/upload')}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all"
            >
              Upload Dataset
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              My Datasets
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              {datasets.length} dataset{datasets.length !== 1 ? 's' : ''} available
            </p>
          </div>
          <button
            onClick={() => navigate('/upload')}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all"
          >
            Upload New Dataset
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Datasets Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 space-y-2">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Your Datasets</span>
              </h3>
              {datasets.map((dataset) => (
                <div
                  key={dataset.id}
                  onClick={() => {
                    setSelectedDataset(dataset);
                    setCurrentPage(1);
                  }}
                  className={`p-3 rounded-lg cursor-pointer transition-all group ${
                    selectedDataset?.id === dataset.id
                      ? 'bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-500'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700 border-2 border-transparent'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white text-sm truncate flex-1">
                      {dataset.filename}
                    </h4>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteDataset(dataset.id);
                      }}
                      className="ml-2 p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(dataset.upload_date)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {selectedDataset && (
              <>
                {/* Dataset Info */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                    {selectedDataset.filename}
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rows</div>
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {selectedDataset.row_count?.toLocaleString()}
                      </div>
                    </div>
                    <div className="p-4 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Columns</div>
                      <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                        {selectedDataset.column_count}
                      </div>
                    </div>
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Size</div>
                      <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        {(selectedDataset.file_size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/30 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Uploaded</div>
                      <div className="text-sm font-bold text-green-600 dark:text-green-400">
                        {formatDate(selectedDataset.upload_date)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* View Toggle */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 mb-6">
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                      <button
                        onClick={() => setViewMode('table')}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${
                          viewMode === 'table'
                            ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow'
                            : 'text-gray-600 dark:text-gray-400'
                        }`}
                      >
                        <FileText className="h-5 w-5 inline mr-2" />
                        Table View
                      </button>
                      <button
                        onClick={() => setViewMode('chart')}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${
                          viewMode === 'chart'
                            ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow'
                            : 'text-gray-600 dark:text-gray-400'
                        }`}
                      >
                        <TrendingUp className="h-5 w-5 inline mr-2" />
                        Chart View
                      </button>
                    </div>

                    {viewMode === 'chart' && (
                      <div className="flex flex-wrap gap-3 flex-1">
                        <select
                          value={chartConfig.type}
                          onChange={(e) => setChartConfig({ ...chartConfig, type: e.target.value })}
                          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="bar">Bar Chart</option>
                          <option value="line">Line Chart</option>
                          <option value="pie">Pie Chart</option>
                        </select>

                        <select
                          value={chartConfig.column}
                          onChange={(e) => setChartConfig({ ...chartConfig, column: e.target.value })}
                          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="">Select Column</option>
                          {getColumns().map((col) => (
                            <option key={col} value={col}>
                              {col}
                            </option>
                          ))}
                        </select>

                        <select
                          value={chartConfig.aggregation}
                          onChange={(e) => setChartConfig({ ...chartConfig, aggregation: e.target.value })}
                          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="count">Count</option>
                          <option value="sum">Sum</option>
                          <option value="avg">Average</option>
                          <option value="min">Minimum</option>
                          <option value="max">Maximum</option>
                        </select>
                      </div>
                    )}
                  </div>
                </div>

                {/* Data Display */}
                {viewMode === 'table' ? (
                  <DataTable
                    data={tableData}
                    columns={getColumns()}
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                  />
                ) : (
                  chartData && chartConfig.column ? (
                    <ChartView
                      data={chartData}
                      type={chartConfig.type}
                      xKey={chartConfig.column}
                      yKey={chartConfig.aggregation}
                    />
                  ) : (
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
                      <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500 dark:text-gray-400">
                        Select a column to generate chart
                      </p>
                    </div>
                  )
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
