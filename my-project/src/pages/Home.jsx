import { Link } from 'react-router-dom';
import { BarChart3, Upload, Zap, Shield, TrendingUp, Database } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="text-center animate-fade-in">
            <div className="inline-flex items-center justify-center p-2 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-6">
              <BarChart3 className="h-12 w-12 text-blue-600 dark:text-blue-400" />
            </div>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-gray-900 dark:text-white mb-6">
              <span className="block">Transform Your Data</span>
              <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Into Insights
              </span>
            </h1>
            <p className="max-w-3xl mx-auto text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-10">
              Upload, visualize, and analyze your data with powerful interactive charts and tables.
              No coding required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/signup"
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-200"
              >
                Get Started Free
              </Link>
              <Link
                to="/signin"
                className="px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-xl font-semibold text-lg border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 transition-all duration-200"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>

        {/* Decorative background elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Why Choose DataViz Pro?
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Everything you need to make data-driven decisions
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: <Upload className="h-8 w-8" />,
              title: 'Easy Upload',
              description: 'Drag and drop CSV or Excel files. Support for large datasets with instant processing.',
              color: 'from-blue-500 to-blue-600'
            },
            {
              icon: <BarChart3 className="h-8 w-8" />,
              title: 'Interactive Charts',
              description: 'Beautiful visualizations with bar charts, line graphs, and pie charts. Fully interactive.',
              color: 'from-indigo-500 to-indigo-600'
            },
            {
              icon: <Database className="h-8 w-8" />,
              title: 'Smart Tables',
              description: 'Sort, filter, and paginate through your data with lightning-fast performance.',
              color: 'from-purple-500 to-purple-600'
            },
            {
              icon: <Zap className="h-8 w-8" />,
              title: 'Real-time Processing',
              description: 'Backend-powered data processing ensures accuracy and speed for all operations.',
              color: 'from-yellow-500 to-yellow-600'
            },
            {
              icon: <Shield className="h-8 w-8" />,
              title: 'Secure & Private',
              description: 'Your data is encrypted and stored securely. Full authentication and authorization.',
              color: 'from-green-500 to-green-600'
            },
            {
              icon: <TrendingUp className="h-8 w-8" />,
              title: 'Advanced Analytics',
              description: 'Aggregations, summaries, and statistical insights powered by AI.',
              color: 'from-red-500 to-red-600'
            }
          ].map((feature, index) => (
            <div
              key={index}
              className="group bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300 animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className={`inline-flex p-3 bg-gradient-to-r ${feature.color} rounded-xl text-white mb-4 group-hover:scale-110 transition-transform`}>
                {feature.icon}
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl shadow-2xl overflow-hidden">
          <div className="px-8 py-16 sm:px-16 text-center">
            <h2 className="text-4xl font-extrabold text-white mb-6">
              Ready to visualize your data?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join thousands of users who are making smarter decisions with DataViz Pro.
              Start your journey today.
            </p>
            <Link
              to="/signup"
              className="inline-block px-10 py-4 bg-white text-blue-600 rounded-xl font-bold text-lg hover:bg-gray-100 transform hover:scale-105 transition-all duration-200 shadow-xl"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
