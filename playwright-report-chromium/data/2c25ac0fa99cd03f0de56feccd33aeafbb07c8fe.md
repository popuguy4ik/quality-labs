# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: visual.spec.ts >> Визуальные тесты >> первый экран: contacts
- Location: e2e/visual.spec.ts:8:5

# Error details

```
Error: A snapshot doesn't exist at /home/runner/work/quality-labs/quality-labs/lab5/e2e/__screenshots__/chromium/contacts.png, writing actual.
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - link "Перейти к содержимому" [ref=e2] [cursor=pointer]:
    - /url: "#main"
  - banner [ref=e3]:
    - generic [ref=e4]:
      - link "Сова, на главную" [ref=e5] [cursor=pointer]:
        - /url: index.html
        - generic [ref=e6]: Сова
      - navigation "Основная навигация" [ref=e7]:
        - link "Возможности" [ref=e8] [cursor=pointer]:
          - /url: features.html
        - link "Команда" [ref=e9] [cursor=pointer]:
          - /url: team.html
        - link "Блог" [ref=e10] [cursor=pointer]:
          - /url: blog.html
        - link "Контакты" [ref=e11] [cursor=pointer]:
          - /url: contacts.html
      - generic [ref=e12]:
        - button "Включить тёмную тему" [ref=e13] [cursor=pointer]
        - link "Войти" [ref=e16] [cursor=pointer]:
          - /url: feature.html
        - link "Скачать" [ref=e17] [cursor=pointer]:
          - /url: index.html#download
  - main [ref=e18]:
    - region "Связаться с нами" [ref=e19]:
      - generic [ref=e20]:
        - navigation "Хлебные крошки" [ref=e21]:
          - list [ref=e22]:
            - listitem [ref=e23]:
              - link "Главная" [ref=e24] [cursor=pointer]:
                - /url: index.html
            - listitem [ref=e25]:
              - generic [ref=e26]: Контакты
        - heading "Связаться с нами" [level=1] [ref=e27]
        - paragraph [ref=e28]: Ответим на вопросы о Сове, поможем с переносом чатов и выслушаем предложения. Обычно отвечаем в течение дня.
    - generic [ref=e30]:
      - generic [ref=e32]:
        - heading "Написать в поддержку" [level=2] [ref=e33]
        - generic [ref=e34]:
          - generic [ref=e35]:
            - generic [ref=e36]: Имя
            - textbox "Имя" [ref=e37]:
              - /placeholder: Как к вам обращаться
          - generic [ref=e38]:
            - generic [ref=e39]: Почта
            - textbox "Почта" [ref=e40]:
              - /placeholder: name@mail.ru
          - generic [ref=e41]:
            - generic [ref=e42]: Тема
            - combobox "Тема" [ref=e44] [cursor=pointer]:
              - option "Вопрос по приложению" [selected]
              - option "Перенос чатов"
              - option "Проблема со звонками"
              - option "Сотрудничество"
              - option "Другое"
          - generic [ref=e45]:
            - generic [ref=e46]: Сообщение
            - textbox "Сообщение" [ref=e47]:
              - /placeholder: Опишите вопрос, чем подробнее, тем лучше
            - paragraph [ref=e48]: Не пишите пароли и коды из СМС, мы никогда их не спрашиваем.
          - generic [ref=e50] [cursor=pointer]:
            - checkbox "Согласен на обработку персональных данных для ответа на обращение" [ref=e51]
            - generic [ref=e52]: Согласен на обработку персональных данных для ответа на обращение
          - button "Отправить" [ref=e54] [cursor=pointer]
      - complementary "Как нас найти" [ref=e57]:
        - heading "Как нас найти" [level=2] [ref=e58]
        - list [ref=e59]:
          - listitem [ref=e60]:
            - generic [ref=e64]:
              - strong [ref=e65]: Офис
              - text: Москва, Большой Саввинский переулок, 12
          - listitem [ref=e66]:
            - generic [ref=e70]:
              - strong [ref=e71]: Почта
              - link "hello@sova.example" [ref=e72] [cursor=pointer]:
                - /url: mailto:hello@sova.example
          - listitem [ref=e73]:
            - generic [ref=e77]:
              - strong [ref=e78]: Телефон
              - link "8 800 000-00-00" [ref=e79] [cursor=pointer]:
                - /url: tel:+78000000000
          - listitem [ref=e80]:
            - generic [ref=e84]:
              - strong [ref=e85]: Поддержка
              - text: Каждый день с 9:00 до 21:00
        - iframe [ref=e87]:
          - generic [ref=f1e2]:
            - generic:
              - region "Map" [ref=f1e3]
              - button "Map marker" [ref=f1e4]
            - generic:
              - generic [ref=f1e8]:
                - button "Zoom In" [ref=f1e9] [cursor=pointer]
                - button "Zoom Out" [ref=f1e11] [cursor=pointer]
              - group [ref=f1e13]:
                - generic [ref=f1e14]:
                  - text: ©
                  - link "OpenStreetMap contributors" [ref=f1e15] [cursor=pointer]:
                    - /url: /copyright
                  - text: ♥️
                  - link "Make a Donation" [ref=f1e16] [cursor=pointer]:
                    - /url: https://supporting.openstreetmap.org
                  - text: .
                  - link "Website and API terms" [ref=f1e17] [cursor=pointer]:
                    - /url: https://wiki.osmfoundation.org/wiki/Terms_of_Use
  - contentinfo [ref=e88]:
    - generic [ref=e89]:
      - generic [ref=e90]:
        - generic [ref=e91]:
          - link "Сова, на главную" [ref=e92] [cursor=pointer]:
            - /url: index.html
            - generic [ref=e93]: Сова
          - paragraph [ref=e94]: Мессенджер со сквозным шифрованием, который работает даже на слабом интернете.
          - generic [ref=e95]:
            - link "Написать нам на почту" [ref=e96] [cursor=pointer]:
              - /url: mailto:hello@sova.example
            - link "Блог Совы" [ref=e99] [cursor=pointer]:
              - /url: blog.html
            - link "Поддержка" [ref=e102] [cursor=pointer]:
              - /url: contacts.html
        - navigation "Продукт" [ref=e105]:
          - heading "Продукт" [level=2] [ref=e106]
          - list [ref=e107]:
            - listitem [ref=e108]:
              - link "Возможности" [ref=e109] [cursor=pointer]:
                - /url: features.html
            - listitem [ref=e110]:
              - link "Веб-версия" [ref=e111] [cursor=pointer]:
                - /url: feature.html
            - listitem [ref=e112]:
              - link "Скачать" [ref=e113] [cursor=pointer]:
                - /url: index.html#download
        - navigation "Компания" [ref=e114]:
          - heading "Компания" [level=2] [ref=e115]
          - list [ref=e116]:
            - listitem [ref=e117]:
              - link "Команда" [ref=e118] [cursor=pointer]:
                - /url: team.html
            - listitem [ref=e119]:
              - link "Блог" [ref=e120] [cursor=pointer]:
                - /url: blog.html
            - listitem [ref=e121]:
              - link "Контакты" [ref=e122] [cursor=pointer]:
                - /url: contacts.html
        - navigation "Помощь" [ref=e123]:
          - heading "Помощь" [level=2] [ref=e124]
          - list [ref=e125]:
            - listitem [ref=e126]:
              - link "Поддержка" [ref=e127] [cursor=pointer]:
                - /url: contacts.html
            - listitem [ref=e128]:
              - link "Как работает шифрование" [ref=e129] [cursor=pointer]:
                - /url: post.html
            - listitem [ref=e130]:
              - link "hello@sova.example" [ref=e131] [cursor=pointer]:
                - /url: mailto:hello@sova.example
      - generic [ref=e132]:
        - paragraph [ref=e133]: © 2026 Сова
        - paragraph [ref=e134]: Учебный проект, ЛР № 3 по веб-дизайну
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | // Визуальная регрессия: сравнение с эталонными скриншотами (только Chromium)
  4  | test.describe('Визуальные тесты', () => {
  5  |   test.use({ viewport: { width: 1280, height: 800 } });
  6  | 
  7  |   for (const [name, path] of [['home', '/'], ['features', '/features.html'], ['contacts', '/contacts.html']]) {
  8  |     test(`первый экран: ${name}`, async ({ page }) => {
  9  |       await page.emulateMedia({ colorScheme: 'light', reducedMotion: 'reduce' });
  10 |       await page.route('**/openstreetmap.org/**', (r) => r.abort());
  11 |       await page.goto(path);
  12 |       await page.evaluate(() => document.fonts.ready);
> 13 |       await expect(page).toHaveScreenshot(`${name}.png`);
     |       ^ Error: A snapshot doesn't exist at /home/runner/work/quality-labs/quality-labs/lab5/e2e/__screenshots__/chromium/contacts.png, writing actual.
  14 |     });
  15 |   }
  16 | });
  17 | 
```