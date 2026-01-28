# Default parse_mode is HTML

phrases = {
    # Global
    'botFullName_ru': "I.T.K Симулятор Казино", 'botFullName_en': "I.T.K Casino Simulator", 
    'emojiFlag_ru': "🇷🇺", 'emojiFlag_en': "🇬🇧",
    'languageCode_ru': "🇷🇺 Русский", 'languageCode_en': "🇬🇧 English",
    'language_ru': "язык", 'language_en': "language",

    'youAreBanned_ru': "<b>Вы забанены в боте.</b>", 'youAreBanned_en': "<b>You are banned in the bot.</b>",
    'tryAgain_ru': "Попробуйте снова", 'tryAgain_en': "Try again",

    'on_ru': "вкл.", 'on_en': "on",
    'off_ru': "откл.", 'off_en': "off",
    'Im_ru': "Я", 'Im_en': "I'm",

    # Handlers
    'asAdminYouCanList_ru': (
        "<b>Как администратор вы можете:</b>\n<blockquote>"
        "⦁ Создавать свои \"ставки\", управлять коэффицентом.\n"
        "⦁ Создавать предметы для магазина своего чата, добавлять им эффекты от использования.\n"
        "⦁ Создавать свою иерархию \"модерации\" <i>(управление \"ставками\", магазином)</i>: свои названия и доступные права.</blockquote>"
    ),
    'asAdminYouCanList_en': (
        "<b>As an administrator you can:</b>\n<blockquote>"
        "⦁ Create your own \"bets\", manage the odds.\n"
        "⦁ Create items for your chat shop, add effects to them from using.\n"
        "⦁ Create your own hierarchy of \"moderation\" <i>(managing \"bids\", the store)</i>: your own names and available rights.</blockquote>"
    ),
    'asUserYouCanList_ru': (
        "<b>Пользователь может:</b>\n<blockquote>"
        "⦁ Играть в \"казино\", делать ставки на \"турнирах\".\n"
        "⦁ Покупать предметы из магазина чата.\n"
        "⦁ В теории возможно даже отыгрывать ролеплей.</blockquote>"
    ),
    'asUserYouCanList_en': (
        "<b>As user:</b>\n<blockquote>"
        "⦁ Play at \"casino\", place bets on \"tournaments\".\n"
        "⦁ Buy items from chat store.\n"
        "⦁ In theory, it's possible to roleplay with this bot.</blockquote>"
    ),
    'justTryIt_ru': "Просто опробуйте, протестируйте", 'justTryIt_en': "Just try it",
    'switchTo_ru': "Переключиться на", 'switchTo_en': "Switch to",

    'greeting1_ru': "Приветствую", 'greeting2_ru': "Всем здравия", 'greeting3_ru': "Как дела",
    'greeting1_en': "Greeting", 'greeting2_en': "Greetings everyone", 'greeting3_en': "How are you",
    'enterHelp_ru': "Для получения краткой справки введите",
    'enterHelp_en': "For a quick reference, enter",

    'help_ru': "помощь", 'help_en': "help",
    'settings_ru': "настройки", 'settings_en': "settings",
    'ifYouKickBot_ru': "Если вы кикните бота из группы, то он безвозвратно забудет всю вашу статистику, настройки и так далее.",
    'ifYouKickBot_en': "If you kick a bot from a group, it will permanently forget all your stats, settings, and so on.",

    'profile_ru': "профиль", 'profile_en': "profile",
    'adminLevel_ru': "уровень админки", 'adminLevel_en': "admin level",
    'wins_ru': "Побед", 'wins_en': "Wins", 'loses_ru': "Проигрышей", 'loses_en': "Loses",
    'balanceWithoutLoses_ru': "Если бы этот человек ничего не тратил и ни разу не проигрывал, то его баланс составлял бы",
    'balanceWithoutLoses_en': "If this person hadn't spent anything and never lost, then his balance would be",
    'activeBonus_ru': "Активный бонус", 'activeBonus_en': "Active bonus",
    'lastPlay_ru': "Играл в последний раз", 'lastPlay_en': "Last play",

    'languageSwitched_ru': "Язык переключён на", 'languageSwitched_en': "Language switched to",
    'mainDeveloper_ru': "Разработчик кода", 'mainDeveloper_en': "Code developer",

    # Callbacks
    'fsmChatSettingsEmoji_ru': "Отправьте в следующем сообщении эмодзи, который будет использоваться для обозначение этой группы.",
    'fsmChatSettingsEmoji_en': "Send in the next message the emoji that will be used to identify this group.",
    'fsmChatSettingsEmojiError_ru': "Отправьте один эмодзи!", 'fsmChatSettingsEmojiError_en': "Send one emoji!",
    'fsmChatSettingsPrefix_ru': "Отправьте в следующем сообщении префикс для всех команд этого бота или введите <code>убрать</code>.",
    'fsmChatSettingsPrefix_en': "Send the prefix for all commands of this bot in the following message or enter <code>reset</code>.",
    'fsmChatSettingsPrefixError_ru': "Размер префикса должен быть не больше 1 символа!",
    'fsmChatSettingsPrefixError_en': "The prefix size should be no more than 1 character!",
    'fsmChatSettingsPrefixEmojiError_ru': "Префикс не может быть эмодзи!",
    'fsmChatSettingsPrefixEmojiError_en': "The prefix cannot be an emoji!",
    'fsmChatSettingsCooldown_ru': "Отправьте в следующем сообщении время в секундах <i>(не более 60)</i>, раз в которое люди смогут вводить игровые команды.",
    'fsmChatSettingsCooldown_en': "In the following message, send the time in seconds <i>(no more than 60)</i> at which people can enter game commands.",
    'fsmChatSettingsCooldownValueError_ru': "Отправьте число!", 'fsmChatSettingsCooldownValueError_en': "Send a number!",
    'fsmChatSettingsCooldownWrongRangeError_ru': "Отправьте число от 0 до 60!", 'fsmChatSettingsCooldownWrongRangeError_en': "Send a number from 0 to 60!",

    # Keyboards
    'addToChat_ru': "Добавить в свой чат", 'addToChat_en': "Add to your chat",
    'prefix_ru': "Префикс команд", 'prefix_en': "Commands prefix",
    'prefixEmpty_ru': "нет префикса", 'prefixEmpty_en': "no prefix",
    'chatEmoji_ru': "Эмодзи чата", 'chatEmoji_en': "Emoji of the chat",
    'cooldown_ru': "Кулдаун", 'cooldown_en': "Cooldown", 'sec_ru': "сек.", 'sec_en': "sec",
    'isBannedFalse_ru': "Временно выключить бота", 'isBannedFalse_en': "Temporarily disable the bot",
    'isBannedTrue_ru': "Включить бота обратно", 'isBannedTrue_en': "Turn the bot back on"
}