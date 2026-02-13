import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main(): 
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # 获取所有页面的列表
    all_pages = list(corpus.keys())
    N = len(all_pages)
    
    # 初始化概率分布，所有页面初始概率为0
    prob_dist = {page: 0 for page in all_pages}
    
    # 获取当前页面的出链
    links = corpus[page]
    
    # 处理无出链页面：视为链接到所有页面
    if len(links) == 0:
        links = set(all_pages)
    
    # 第一部分：随机跳转概率 (1-d)/N，所有页面都获得
    random_prob = (1 - damping_factor) / N
    
    # 第二部分：跟随链接的概率 d/len(links)，只给链接到的页面
    link_prob = damping_factor / len(links)
    
    # 分配概率
    for p in all_pages:
        prob_dist[p] = random_prob  # 每个页面都有基础概率
        if p in links:  # 如果在当前页面的出链中，额外加上链接概率
            prob_dist[p] += link_prob
    
    # 验证概率和为1（考虑浮点误差）
    total = sum(prob_dist.values())
    assert abs(total - 1.0) < 1e-10, f"Probability sum is {total}, not 1"
    
    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # 获取所有页面列表
    pages = list(corpus.keys())
    
    # 初始化访问计数器
    visits = {page: 0 for page in pages}
    
    # 第一个样本：随机选择一个页面
    current_page = random.choice(pages)
    visits[current_page] = 1
    
    # 生成剩余的 n-1 个样本
    for _ in range(n - 1):
        # 获取从当前页面的转移概率分布
        prob_dist = transition_model(corpus, current_page, damping_factor)
        
        # 根据概率分布选择下一个页面
        next_page = random.choices(
            list(prob_dist.keys()),
            weights=list(prob_dist.values())
        )[0]
        
        # 更新计数和当前页面
        visits[next_page] += 1
        current_page = next_page
    
    # 计算每个页面的PageRank（出现频率）
    pagerank = {page: count / n for page, count in visits.items()}
    
    # 验证概率和为1
    total = sum(pagerank.values())
    assert abs(total - 1.0) < 1e-10, f"PageRank sum is {total}, not 1"
    
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    N = len(pages)
    
    # 预处理：出链数量
    num_links = {}
    for page in pages:
        links = corpus[page]
        num_links[page] = N if len(links) == 0 else len(links)
    
    # 预处理：入链来源
    inlinks = {page: [] for page in pages}
    for page in pages:
        for candidate in pages:
            if page in corpus[candidate] or len(corpus[candidate]) == 0:
                inlinks[page].append(candidate)
    
    # 初始化
    pagerank = {page: 1 / N for page in pages}
    
    # 使用收敛标志控制循环
    converged = False
    
    while not converged:
        new_pagerank = {}
        max_change = 0
        
        for page in pages:
            rank = (1 - damping_factor) / N
            
            for candidate in inlinks[page]:
                rank += damping_factor * (
                    pagerank[candidate] / num_links[candidate]
                )
            
            new_pagerank[page] = rank
            change = abs(new_pagerank[page] - pagerank[page])
            max_change = max(max_change, change)
        
        # 检查是否收敛
        converged = max_change < 0.001
        pagerank = new_pagerank
    
    # 归一化
    total = sum(pagerank.values())
    pagerank = {page: rank / total for page, rank in pagerank.items()}
    
    return pagerank


if __name__ == "__main__":
    main()
