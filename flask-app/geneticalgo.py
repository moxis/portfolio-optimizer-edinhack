from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
from statistics import *
from random import randint, shuffle
import numpy as np, numpy.random

class GA:
    def __init__(self, stocks):
        self.stocks = stocks
        self.n_generations = 100
        self.data = {}
        self.data_returns = {}
        self.size = len(stocks)
        self.population_size = 50
        self.population = self.generate_population(self.population_size)
        self.elite_size = 2

        for stock in self.stocks:
            self.data[stock] =  share.Share(stock).get_historical(share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_MONTH, 1)["close"][1:]

        for stock in self.stocks:
            prices = self.data[stock]
            self.data_returns[stock] = []
            for i in range(1, len(prices)):
                price = prices[i]
                previous_price = prices[i - 1]
                returns = (price - previous_price) / previous_price
                self.data_returns[stock].append(returns)
        
    def portfolio_returns(self, chromosome):
        returns = []
        total = sum(chromosome)
        length = len(self.data_returns[self.stocks[0]])

        for i in range(length):
            result = 0
            for j in range(self.size):
                result += (chromosome[j] / total) * self.data_returns[self.stocks[j]][i]
            
            returns.append(result)

        return returns

    def sharpe(self, chromosome):
        returns = self.portfolio_returns(chromosome)
        return ((mean(returns))/stdev(returns))
    
    def generate_population(self, size):
        population = []
        for chromosome in list(np.random.dirichlet(np.ones(self.size),size=size)):
            population.append(list(chromosome))

        return population
    
    def mutate(self, chromosome):
        if randint(1, 2) == 1:
            random_index = randint(0, len(chromosome)-1)
            chromosome[random_index] = np.random.uniform(0, 1)
        else:
            shuffle(chromosome)

        return chromosome
    
    def crossover(self, parent1, parent2):
        random_index = randint(0, self.size - 1)
        return parent1[0:random_index] + parent2[random_index:]
    
    def selection(self):
        fighters = []
        for x in range(2):
            fighters.append(self.population[randint(0, len(self.population)-1)])
        
        best_fighter = fighters[0]
        for fighter in fighters[1:]:
            if self.sharpe(fighter) > self.sharpe(best_fighter):
                best_fighter = fighter
        
        return best_fighter
    
    def get_highest_fitness(self):
        return max(self.population, key=self.sharpe)
    
    def natural_selection(self):
        self.population = sorted(self.population, key=self.sharpe, reverse=True)
        for i in range(1, self.n_generations + 1):
            fittest = self.get_highest_fitness()

            new_population = self.population[0:self.elite_size]
            for j in range(self.population_size - self.elite_size):
                parent1 = self.selection()
                parent2 = self.selection()
                child = self.crossover(parent1, parent2)

                if randint(1, 100) <= 5:
                    child = self.mutate(child)
                
                new_population.append(child)

            self.population = sorted(new_population, key=self.sharpe, reverse=True)
        
        return fittest
    
    def get_portfolio(self, fittest):
        results = {}
        total = sum(fittest)
        for i in range(self.size):
            results[self.stocks[i]] = round(fittest[i]/total * 100, 2)
        
        return results
    
    def get_returns(self, fittest, capital):
        results = {}
        total = sum(fittest)

        for i in range(len(self.stocks)):
            results[self.stocks[i]] = sum(self.data_returns[self.stocks[i]]) * (fittest[i] / total) * capital
        
        return results
    
    def get_performance(self, fittest, capital):
        results = {}
        for stock in self.stocks:
            length = len(self.data_returns[stock])
            starting_balance = capital
            results[stock] = []
            for change in self.data_returns[stock]:
                starting_balance *= (1 + change)
                results[stock].append(starting_balance)
        
        results["ga"] = []
        returns = self.portfolio_returns(fittest)

        starting_balance = capital
        for change in returns:
            starting_balance *= (1 + change)
            results["ga"].append(starting_balance)

        return results

        



