import numpy as np
from misc.sigmoid import *
from distributions.basemodel import *


class LogLogistic(Base):
    '''
    The log logistic distribution: https://en.wikipedia.org/wiki/Log-logistic_distribution
    Since we have alpha as the shape parameter and beta as the scale parameter
    in the link above while k for shape and lmb for scale more generally,
    the instance of this distribution will have alpha=k always
    and beta=lmb always.
    '''
    def __init__(self, alp=1, beta=0.5, ti = None, xi = None, params=np.array([500,5]), gamma=0, params0=np.array([167.0, 0.3]), verbose=False):
        '''
        Initializes an instance of the log logistic distribution.
        '''
        if ti is not None:
            self.train_org = ti
            self.train_inorg = xi
            self.gradient_descent(params = params, gamma=gamma, params0=params0, verbose=verbose)
        else:
            self.train = []
            self.test = []
            self.train_org = []
            self.train_inorg = []
            self.alpha = self.lmb = alpha
            self.beta = self.k = beta
            self.params = []

    def set_params(self, alpha, beta, params=None):
        if params is not None:
            [alpha, beta] = params[:2]
        self.k = self.beta = beta
        self.lmb = self.alpha = alpha
        self.params = [alpha, beta]

    def determine_params(self, k, lmb, params):
        '''
        Determines the parameters. Defined in basemodel.py
        '''
        return super(LogLogistic, self).determine_params(k, lmb, params)

    def pdf(self,x,alpha=None,beta=None):
        '''
        Returns the probability density function of the distribution.
        args:
            x: The value at which the PDF is to be calculated.
            alpha: The shape paramter.
            beta: The scale parameter.
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return (beta/alpha)*(x/alpha)**(beta-1)/(1+(x/alpha)**beta)**2

    def cdf(self,x,alpha=None,beta=None):
        '''
        The cumulative density function.
        args:
            x: The value at which the CDF is to be calculated.
            alpha: The shape parameter of the distribution.
            beta: The scale parameter of the distribution.
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return 1/(1+(x/alpha)**-beta)

    def inv_cdf(self, u, alpha=None, beta=None):
        '''
        The inverse CDF of the dsitribution (used for generating random samples).
        args:
            u: A number between 0 and 1.
            alpha: The shape parameter.
            beta: The scale parameter.            
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return alpha*(1/u - 1)**(-1/beta)

    def samples(self, size=1000, alpha=None, beta=None):
        '''
        Generates samples from a log logistic distribution.
        args:
            size: The number of samples to be generated.
            alpha: The shape parameter of the distribution.
            beta: The scale parameter of the distribution.
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return self.inv_cdf(np.random.uniform(size=size), alpha, beta)

    def logpdf(self,x,alpha,beta):
        '''
        The logarithm of the PDF of the distribution.
        args:
            x: The value at which the function is to be evaluated.
            alpha: The shape parameter.
            beta: The scale parameter.            
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return np.log(beta)-np.log(alpha) +(beta-1)*(np.log(x) - np.log(alpha)) - 2*np.log(1+(x/alpha)**beta)

    def survival(self,x,alpha=None,beta=None):
        '''
        The survival function of the distribution (probability that it is greater than x).
        args:
            x: Evaluated here.
            alpha: Shape parameter.
            beta: Scale parameter.            
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return 1-self.cdf(x,alpha,beta)

    def logsurvival(self,x,alpha,beta):
        '''
        The logarithm of the survival function of the distribution (probability that it is greater than x).
        For now, we simply take the log, but we can possibly improve the efficiency numerically in the future.
        args:
            x: Evaluated here.
            alpha: Shape parameter.
            beta: Scale parameter.            
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return np.log(self.survival(x,alpha,beta))

    def loglik(self,t,x,alpha,beta):
        '''
        The log likelihood of the loglogistic distribution.
        args:
            t: The array of observed survival times.
            x: The array of censored survival times.
            alpha: The shape parameter.
            beta: The scale parameter.
        '''
        [beta, alpha] = self.determine_params(beta, alpha, None)
        return sum(self.logpdf(t,alpha,beta)) + sum(self.logsurvival(x,alpha,beta))

    def grad(self,t,x,alp=None,beta=None):
        '''
        Analytically calculates the gradient.
        args:
            t: The array of observed survival times.
            x: The array of censored survival times.
            k: The shape parameter.
            lmb: The scale parameter.
        '''
        n = len(t)
        m = len(x)
        delalp = -n*beta/alp +2*beta/alp**(beta+1) * sum(t**beta/(1+(t/alp)**beta)) + beta/alp**(beta+1)*sum(x**beta/(1+(x/alp)**beta))
        delbeta = n/beta -n*np.log(alp) + sum(np.log(t)) -2*sum((t/alp)**beta/(1+(t/alp)**beta)*np.log(t/alp) ) - sum((x/alp)**beta/(1+(x/alp)**beta)*np.log(x/alp))
        return np.array([delalp,delbeta])

    def hessian(self,t,x,k=0.5,lmb=0.3):
        '''
        TODO: Calculate the hessian matrix of the log likelihood function
        instead of defaulting to the numerical version.
        args:
            t: The array of observed survival times.
            x: The array of censored survival times.
            k: The shape parameter.
            lmb: The scale parameter.
        '''
        return self.numerical_hessian(t,x,k,lmb)

    

## These are old methods. Ignore them.
def fixedAlp(beta):
    alp = 79.82
    return ll.grad(ll.train_org,ll.train_inorg,alp,beta)[1]

def fixedBeta(alp):
    beta = 1.35
    return ll.grad(ll.train_org,ll.train_inorg,alp,beta)[0]



