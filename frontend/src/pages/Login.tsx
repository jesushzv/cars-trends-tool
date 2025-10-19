import React, { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const { login, isAuthenticated, loading } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const location = useLocation();
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

  const from = location.state?.from?.pathname || '/dashboard';

  if (loading) {
    return <LoadingSpinner className="min-h-screen" />;
  }

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  const onSubmit = async (data: LoginForm) => {
    setIsSubmitting(true);
    try {
      await login(data.username, data.password);
      toast.success('Login successful!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Car Trends Analysis Tool
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="label">
                Username
              </label>
              <input
                {...register('username', { required: 'Username is required' })}
                type="text"
                className="input"
                placeholder="Enter your username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="password" className="label">
                Password
              </label>
              <input
                {...register('password', { required: 'Password is required' })}
                type="password"
                className="input"
                placeholder="Enter your password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary w-full flex justify-center items-center"
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Default credentials: admin / admin123
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
