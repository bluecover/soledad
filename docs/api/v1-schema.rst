API v1 实体模型
---------------

账户管理
~~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.accounts.UserSchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.MaskedNameSchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.IdentityVoucherSchema
   :members:

请求实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.accounts.RegisterSchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.RegisterVerifySchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.ResetPasswordSchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.ResetPasswordSmsVerifySchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.IdentityVerifySchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.SetNewPasswordSchema
   :members:

.. autoclass:: jupiter.views.api.v1.accounts.ChangePasswordSchema
   :members:


用户信息
~~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.profile.BankCardSchema
   :members:

.. autoclass:: jupiter.views.api.v1.profile.ProfileSchema
   :members:

.. autoclass:: jupiter.views.api.v1.profile.NewNotificationCheckSchema
   :members:

请求实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.profile.BankCardRequestSchema
   :members:

.. autoclass:: jupiter.views.api.v1.profile.IdentitySchema
   :members:

.. autoclass:: jupiter.views.api.v1.profile.MobilePhoneSchema
   :members:

.. autoclass:: jupiter.views.api.v1.profile.MobileVerifySchema
   :members:

行政区划和银行数据
~~~~~~~~~~~~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.data.BankSchema
   :members:

.. autoclass:: jupiter.views.api.v1.data.BankIconSchema
   :members:

.. autoclass:: jupiter.views.api.v1.data.DivisionSchema
   :members:

用户返利和礼券
~~~~~~~~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.coupons.CouponKindSchema
   :members:

.. autoclass:: jupiter.views.api.v1.coupons.CouponSchema
   :members:

.. autoclass:: jupiter.views.api.v1.coupons.NewCouponSchema
   :members:

攒钱助手
~~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.savings.ProductSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.SxbProductSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.WrappedProductSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.ProfileSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.ZhiwangOrderSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.YixinOrderSchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.zhiwang.ZhiwangContractSchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.sxb.ProductSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.PreRedeemResponseSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.RedeemResponseSchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.SxbUserAssetResponseSchema
   :members:

值对象
^^^^^^

.. autoclass:: jupiter.views.api.v1.savings.ProfitPeriod
   :members:

.. autoclass:: jupiter.views.api.v1.savings.ProfitPeriodRange
   :members:

.. autoclass:: jupiter.views.api.v1.savings.ProfitPercentRange
   :members:

.. autoclass:: jupiter.views.api.v1.savings.ProfitRate
   :members:

.. autoclass:: jupiter.views.api.v1.products.sxb.OrderSchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.sxb.PurchaseResponseSchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.sxb.PurchaseVerifyResponseSchema
   :members:

请求实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.products.zhiwang.ZhiwangPurchaseSchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.zhiwang.ZhiwangVerifySchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.zhiwang.ZhiwangPurchaseDateSchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.sxb.PurchaseSchema
   :members:

.. autoclass:: jupiter.views.api.v1.products.sxb.VerifySchema
   :members:

.. autoclass:: jupiter.views.api.v1.savings.RedeemSchema
   :members:

零钱包
~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.wallet.TransactionSchema
   :members:

.. autoclass:: jupiter.views.api.v1.wallet.TransactionResultSchema
   :members:

.. autoclass:: jupiter.views.api.v1.wallet.AnnualRateListSchema
   :members:

.. autoclass:: jupiter.views.api.v1.wallet.ProfitItemSchema
   :members:

.. autoclass:: jupiter.views.api.v1.wallet.ProfileSchema
   :members:

.. autoclass:: jupiter.views.api.v1.wallet.DashboardSchema
   :members:

.. autoclass:: jupiter.views.api.v1.wallet.SpecSchema
   :members:

请求实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.wallet.TransactionsRequestSchema
   :members:

.. autoclass:: jupiter.views.api.v1.wallet.BankcardRequestSchema
   :members:

值对象
^^^^^^

.. autoclass:: jupiter.views.api.v1.wallet.AnnualRateItem
   :members:


礼券红包
~~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.welfare.CouponRegulationSchema
   :members:

.. autoclass:: jupiter.views.api.v1.welfare.CouponSchema
   :members:

.. autoclass:: jupiter.views.api.v1.welfare.CouponCollectionSchema
   :members:

.. autoclass:: jupiter.views.api.v1.welfare.CouponKindSchema
   :members:

.. autoclass:: jupiter.views.api.v1.welfare.RedPacketsSchema
   :members:

.. autoclass:: jupiter.views.api.v1.welfare.RedPacketListSchema
   :members:

.. autoclass:: jupiter.views.api.v1.welfare.RedPacketsRecordSchema
   :members:

值对象
^^^^^^

.. autoclass:: jupiter.views.api.v1.welfare.CouponSpecSchema
   :members:

.. autoclass:: jupiter.views.api.v1.welfare.CouponBenefitSchema
   :members:


兑换码
~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.redeemcode.WelfareInfoSchema
   :members:

值对象
^^^^^^

.. autoclass:: jupiter.views.api.v1.redeemcode.FirewoodInfoSchema
   :members:

.. autoclass:: jupiter.views.api.v1.redeemcode.CouponInfoSchema
   :members:


请求实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.redeemcode.RedeemCodeVerifySchema
   :members:


极光推送
~~~~~~~~

实体业务
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.pusher.DeviceSchema
   :members:

.. autoclass:: jupiter.views.api.v1.pusher.PushStatusInformingSchema
   :members:

弹窗广告
~~~~~~~~

业务实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.advert.AdvertSchema
   :members:

请求实体
^^^^^^^^

.. autoclass:: jupiter.views.api.v1.advert.PopUpSchema
   :members:

.. autoclass:: jupiter.views.api.v1.advert.MarkedAsReadSchema
   :members:
