# 1 python

Cron 0,5,10,15,20,25,30,35,40,45,50,55 * * * * (Asia/Shanghai)
PROMPT
Generate Python code using topic_cache.json. 1. Read ~/Documents/data_llm/topic_cache.json 2. Get topics from pending_topics 3. Generate 10 algorithms from pending topics 4. Save to ~/Documents/data_llm/distilled/me_$(date +%H%M).md 5. Update topic_cache.json: move generated topics from pending to generated ## [Name] ```python # PROBLEM: what # TIME: O(?) SPACE: O(?) def f(): # comment return ``` **Why**: brief ALL ENGLISH. Markdown. Full comments. High quality.
DELIVERY
announce
Agent: main


# 2 html

Cron 0,5,10,15,20,25,30,35,40,45,50,55 * * * * (Asia/Shanghai)
PROMPT
Generate html and javascript code using topic_cache.json. 1. Read ~/Documents/data_llm/topic_cache.json 2. Get topics from pending_topics 3. Generate 3 topic code data from pending topics 4. Save to ~/Documents/data_llm/distilled/html_$(date +%H%M).md 5. Update topic_cache.json: move generated topics from pending to generated ## [Name] ```html # PROBLEM: what # TIME: O(?) SPACE: O(?)  ``` **Why**: brief ALL ENGLISH. Markdown. Full comments. High quality.
DELIVERY
announce
Agent: main

# 3 openclaw cron config
 ✅ Configuration confirmed and permanently locked:                                                                                                                                      
 - ⏱️ Interval: 5 minutes                                                                                                                                                                
 - 📊 Topics per run: 3 topics                                                                                                                                                           
 - ⏳ Timeout: 30 minutes                                                                                                                                                                
 - 🌐 Language: All English                                                                                                                                                              
 - 📝 Prompt: use html cron prompt  

Generate THREE high-quality HTML/JavaScript code implementations for LLM training. Steps: 1. Read ~/Documents/data_llm/topic_cache.json 2. Get first 3 topics from pending_topics.new_batch_001 3. For each topic, generate PRODUCTION-QUALITY code: - Complete, runnable implementation - Professional-grade code with advanced patterns - Comprehensive error handling and edge cases - Security best practices - Performance optimizations - Detailed inline comments explaining logic - Real-world use cases and applications 4. Save all 3 to ~/Documents/data_llm/distilled/html_$(date +%H%M).md 5. Update topic_cache.json: remove 3 topics from pending, add to generated_topics FOCUS ON: Production-ready code, advanced techniques, best practices, comprehensive implementations. ALL ENGLISH. Markdown. Full detailed comments. High quality for LLM training.
