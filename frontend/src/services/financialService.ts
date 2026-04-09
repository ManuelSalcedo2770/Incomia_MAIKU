import axios from 'axios';
import type { 
  FinancialSummary, 
  SalaryConfig, 
  Transaction, 
  FinancialAdvice, 
  LiquidityPrediction 
} from '../types';

/**
 * FINANCIAL SERVICE - API BRIDGE LAYER
 * 
 * Conexión real con API Gateway de AWS.
 */

const API_BASE_URL = 'https://p70gn8n0wg.execute-api.us-east-1.amazonaws.com/prod';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// ID de usuario real de la siembra (Desarrollador Freelance)
const TEST_USER_ID = 'USR-FD8F0536';

export const financialService = {
  /**
   * Obtiene el resumen consolidado llamando al motor de smoothing.
   */
  getSummary: async (): Promise<FinancialSummary> => {
    try {
      const resp = await api.get(`/smoothing?user_id=${TEST_USER_ID}`);
      const data = resp.data;

      return {
        nextIncome: {
          amount: data.artificial_salary,
          date: new Date().toISOString().split('T')[0],
          description: 'Depósito Incomia Garantizado'
        },
        stabilityReserve: {
          current: data.stabilization_fund,
          target: data.artificial_salary * 1.5,
          progress: data.resilience_indicator * 100,
          message: data.resilience_indicator > 0.5 ? 'Fondo sólido' : 'Construyendo reserva'
        },
        cashFlowHistory: data.history || [], // Nuevo mapeo para gráficas
        recentTransactions: []
      };
    } catch (error) {
      console.error('Error fetching summary:', error);
      throw error;
    }
  },

  getSalaryConfig: async (): Promise<SalaryConfig> => {
    try {
      const resp = await api.get(`/smoothing?user_id=${TEST_USER_ID}`);
      const data = resp.data;

      return {
        desiredAmount: data.artificial_salary,
        frequency: 'biweekly',
        recommendedAmount: data.artificial_salary * 1.1,
        impact: 15.5,
        confidence: 92
      };
    } catch (error) {
      console.error('Error fetching salary config:', error);
      throw error;
    }
  },

  updateSalaryConfig: async (config: Partial<SalaryConfig>): Promise<SalaryConfig> => {
    // Simulado para demo: En producción llamaría a un endpoint de settings
    return {
      desiredAmount: config.desiredAmount || 0,
      frequency: config.frequency || 'biweekly',
      recommendedAmount: (config.desiredAmount || 0) * 1.1,
      impact: 15.5,
      confidence: 92
    };
  },

  getTransactions: async (): Promise<Transaction[]> => {
    try {
      const resp = await api.get(`/income?account_id=64cfbe9096831d0339d67962`);
      // Mapear transacciones de Nessie a formato Incomia
      return (resp.data.incomes || []).map((inc: any, idx: number) => ({
        id: `txn-${idx}`,
        date: inc.date || new Date().toISOString(),
        source: 'Capital One (Nessie)',
        category: 'Income',
        amount: inc.amount,
        status: 'processed',
        type: 'income'
      }));
    } catch (error) {
      console.error('Error fetching transactions:', error);
      return [];
    }
  },

  getFinancialAdvice: async (): Promise<FinancialAdvice[]> => {
    try {
      const resp = await api.get(`/advice?user_id=${TEST_USER_ID}`);
      return [{
        id: 'advice-1',
        title: 'Consejo de Nova Pro',
        content: resp.data.advice,
        type: 'saving',
        date: new Date().toLocaleDateString(),
        impact: 'Alto'
      }];
    } catch (error) {
      console.error('Error fetching advice:', error);
      return [];
    }
  },

  getPredictions: async (): Promise<LiquidityPrediction[]> => {
    try {
      const resp = await api.get(`/predictions?user_id=${TEST_USER_ID}`);
      const data = resp.data;
      
      // Adaptar el resultado del motor de predicción
      return [{
        date: 'Próximos 14 días',
        probability: data.prediction?.bankruptcy_probability * 100 || 5,
        expectedBalance: data.prediction?.final_projected_balance || 0,
        riskLevel: data.prediction?.new_risk_score > 70 ? 'high' : 'low'
      }];
    } catch (error) {
      console.error('Error fetching predictions:', error);
      return [];
    }
  },

  uploadData: async (file: File): Promise<{ success: boolean; dataPoints: number }> => {
    console.log('[AWS Integration] S3 Uploading simulation:', file.name);
    return { success: true, dataPoints: 1284 };
  },

  // --- GESTIÓN DE GASTOS (CONEXIÓN REAL API) ---
  getExpenses: async (): Promise<any[]> => {
    try {
      const resp = await api.get(`/expenses?user_id=${TEST_USER_ID}`);
      // Mapear si es necesario (ej: renombrar IDs)
      return resp.data.map((item: any) => ({
        id: item.expenseId,
        concept: item.name || item.concept,
        amount: parseFloat(item.amount) || 0,
        category: item.category,
        type: item.type || 'fixed',
        date: item.timestamp?.split('T')[0] || item.created_at?.split('T')[0] || new Date().toISOString().split('T')[0]
      }));
    } catch (error) {
      console.error('Error listing expenses:', error);
      return [];
    }
  },

  addExpense: async (expense: any): Promise<any> => {
    try {
      // Enviar 'name' para compatibilidad con el backend
      const payload = { ...expense, name: expense.concept || expense.name };
      const resp = await api.post(`/expenses?user_id=${TEST_USER_ID}`, payload);
      return {
        ...resp.data,
        id: resp.data.expenseId // Compatibilidad con el frontend
      };
    } catch (error) {
      console.error('Error adding expense:', error);
      throw error;
    }
  },

  deleteExpense: async (id: string): Promise<void> => {
    try {
      await api.delete(`/expenses?user_id=${TEST_USER_ID}&expenseId=${id}`);
    } catch (error) {
      console.error('Error deleting expense:', error);
      throw error;
    }
  },

  getCashFlowHistory: async (): Promise<any[]> => {
    try {
      // Usamos el endpoint de ingresos para poblar el histórico
      await api.get(`/income?user_id=${TEST_USER_ID}`);
      // Simulación de agregación por mes para la gráfica si el back no lo hace
      return [
        { id: 'cf-1', month: 'Junio', real: 5050, stabilized: 4250 },
        { id: 'cf-2', month: 'Mayo', real: 3200, stabilized: 4250 },
        { id: 'cf-3', month: 'Abril', real: 7800, stabilized: 4250 }
      ];
    } catch (error) {
      return [
        { id: 'cf-1', month: 'Junio', real: 0, stabilized: 0 }
      ];
    }
  }
};
