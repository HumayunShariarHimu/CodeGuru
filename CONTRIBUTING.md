# অবদান রাখার নির্দেশনা

CodeGuru-তে বাংলা ভাষায় প্রোগ্রামিং ও সফটওয়্যার ডেভেলপমেন্ট শেখার উপকরণ উন্নত করতে অবদান স্বাগত। ছোট সংশোধন, ভুল তথ্যের নির্ভরযোগ্য সংশোধন, অসম্পূর্ণ অধ্যায় পূরণ, এবং পাঠযোগ্যতার উন্নতিও মূল্যবান।

## কীভাবে শুরু করবেন

1. পরিবর্তনের আগে সংশ্লিষ্ট course বা resource-এর repository এবং বিদ্যমান সূচিপত্র/README পড়ুন। একই বিষয়ের পুনরাবৃত্তি না করে বিদ্যমান পাঠ উন্নত করার চেষ্টা করুন।
2. কাজটি বড় হলে আগে সংশ্লিষ্ট repository-তে Issue খুলে প্রস্তাবটি আলোচনা করুন। ছোট ও স্পষ্ট সংশোধনের ক্ষেত্রে সরাসরি Pull Request পাঠানো যায়।
3. যে repository-তে পরিবর্তন দরকার সেটি নিজের GitHub account-এ fork করুন, আলাদা branch-এ কাজ করুন, তারপর মূল repository-তে Pull Request খুলুন। PR-এ কী বদলেছে এবং কেন দরকার, সংক্ষেপে লিখুন।
4. তথ্য, code example, command এবং link যাচাই করুন। বিদ্যমান formatting ও বাংলা লেখার ধরন বজায় রাখুন; প্রয়োজনে পরিবর্তিত page বা build স্থানীয়ভাবে পরীক্ষা করুন।
5. review feedback পেলে একই branch-এ সংশোধন যোগ করুন। Maintainer-এর review ও merge-এর আগে PR-কে সম্পন্ন ধরে নেবেন না।

## পরিবর্তন স্থানীয়ভাবে যাচাই করবেন যেভাবে

মূল CodeGuru সাইট বা কোর্স পেজের build পরিবর্তন করলে repository-র root directory থেকে নিচের ধাপগুলো চালান। Python 3 লাগবে; প্রথমবার build dependency ইনস্টল করুন:

```bash
python3 -m pip install -r requirements-pages.txt
python3 scripts/build_pages.py --output _site
python3 scripts/build_course_sites.py --content content --output _site/courses
python3 scripts/build_sitemap.py
```

শেষ ধাপে `_site/sitemap.xml` এবং `_site/robots.txt` তৈরি হয়। Build সফল হলে `_site/index.html` ও `_site/courses/python-programming/index.html` খুলে পরিবর্তিত পেজটি দেখুন। `_site/` generated output—এটি commit করবেন না। শুধু কোর্সের source content বদলালে সংশ্লিষ্ট কোর্সের নিজস্ব repository-র contribution নির্দেশনা অনুসরণ করুন।

## ভালো অবদানের মানদণ্ড

- পরিবর্তনটি নির্দিষ্ট পাঠক-সমস্যা সমাধান করে এবং প্রকল্পের শেখার উদ্দেশ্যের সঙ্গে সম্পর্কিত।
- নতুন দাবি বা বাহ্যিক উপকরণ যোগ করলে নির্ভরযোগ্য source এবং প্রয়োজনীয় attribution উল্লেখ করুন। অন্যের লেখা বা ছবি অনুমতি ও উপযুক্ত license ছাড়া কপি করবেন না।
- PR-কে একটি মূল উদ্দেশ্যে সীমিত রাখুন; অপ্রাসঙ্গিক formatting বা generated file পরিবর্তন এড়িয়ে চলুন।
- গোপন তথ্য, ব্যক্তিগত তথ্য, credential বা ক্ষতিকর code commit করবেন না।

CodeGuru-র মূল ওয়েবসাইটের পরিবর্তনের জন্য এই repository-তে PR দিন। কোনো course-এর বিষয়বস্তুর পরিবর্তনের জন্য সেই course-এর নিজস্ব repository ব্যবহার করুন। সন্দেহ হলে [CodeGuru-তে Issue খুলে](https://github.com/HumayunShariarHimu/CodeGuru/issues) আগে জিজ্ঞেস করুন।
