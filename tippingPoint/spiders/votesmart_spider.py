import scrapy
import json
import sys

class AlibabaSpider(scrapy.Spider):
  name="votesmart"
  base_url = 'https://votesmart.org'
  start_urls = [
    'https://votesmart.org/officials/NA/P/national-congressional',
  ]
  levels = ['C','G','L','J','S','K','M','N','H']
  states = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND','OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT','VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY']
  levels_idx = 0
  states_idx = 0
  def parse(self, response):
    template = self.base_url+'/officials/{}/{}'
    candidates_urls = response.css('.candidate-item .span-4 a::attr(href)').extract()
    candidate_names = response.css('.candidate-item .span-4 a span::text').extract()
    print(len(candidate_names))
    for key in range(len(candidates_urls)):
      candidate_url = candidates_urls[key]
      candidate_name = candidate_names[key]
      data = { 'name': candidate_name}
      candidate_url = self.base_url+candidate_url + '?type=P'
      yield scrapy.Request(candidate_url, callback=self.profileCrawl, meta={'data':data})
    
    if self.states_idx < len(self.states):
      nextLink = template.format(self.states[self.states_idx],self.levels[self.levels_idx])
      self.states_idx = self.states_idx + 1
      self.levels_idx = (self.levels_idx + 1) % len(self.levels)
      # print(nextLink)
      yield scrapy.Request(nextLink)
    

  def profileCrawl(self, response):
    # crawl candidate
    histories = response.css('.timeline .article')
    contactInfos = response.css('#contact-information p')
    data = response.meta['data']
    data['url'] = response.url
    contactInfoJSON = {}
    for contactInfo in contactInfos:
      key = contactInfo.css('strong::text').extract()[0]
      value = contactInfos.css('a::text').extract()
      if len(value) > 0:
        value = value[0]
        contactInfoJSON[key] = value
    data['contact'] = contactInfoJSON
    if len(histories) > 0:
      most_recent = histories[0]
      link = most_recent.css('a::attr(href)').extract()[0].strip()
      yield scrapy.Request(self.base_url+link, callback=self.candidatePositionCrawl, meta={'data':data})
    else:
      yield data

  def candidatePositionCrawl(self, response):
    #crawl candidate's political position
    resMeta = response.meta['data']
    questions = response.css('.pct-profile .question-answer')

    positions = []
    for questionRow in questions:
      question = questionRow.css('td.span-12::text').extract()[0]
      answer = questionRow.css('td.span-3::text').extract()[0]
      positions.append({'question':question, 'answer':answer})
    resMeta['positions'] = positions
    yield resMeta