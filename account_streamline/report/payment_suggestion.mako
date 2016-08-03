<style type="text/css">
${css}

.line td {
    text-align: center;
}

.avoid_page_break {
	page-break-inside: avoid;
}

.payment_suggestion_bottom {
    margin-top: 30px;
    padding: 10px 10px 10px 10px;
}

.payment_suggestion_partner {
	clear: both;
    margin-top: 40px;
    margin-bottom: 40px;
}

.payment_suggestion_total, .payment_suggestion_total_main {
    margin-top: 30px;
    padding: 10px 10px 10px 10px;
    border: 1px #000000 solid;
}

.payment_suggestion_total {
    text-align: right;
}

</style>

%for object in objects:
<% setLang(object.voucher_ids[0].partner_id.lang) %>

<% partners = get_partners(object) %>

<!-- Using h2 as the font-size property doesn't seem to affect divs... -->
<h2 class="payment_suggestion_total_main">
	${ _('Journal: %s') % object.voucher_ids[0].journal_id.name }<br/>
	<% voucher_count, partner_count, total = get_totals(partners) %>
	${ _('Voucher count: %d') % voucher_count }<br/>
	${ _('Partner count: %d') % partner_count }<br/>
	${ _('Total: %s') % formatLang(total, currency_obj=object.voucher_ids[0].currency_id) }
</h2>

%for partner, partner_details in partners.iteritems():
<%
	vouchers = partner_details['vouchers']
	partner_total = partner_details['total']
%>

<!-- Page breaks have not been ideally fixed (tables that are too high still span multiple pages
without their report row being repeated) but this solution is already quite good; see
<https://bitbucket.org/xcg/account_streamline/issue/38>. -->
<div class="avoid_page_break">

<h2 class="payment_suggestion_partner">${ partner.name }</h2>

<table class="list_table">
    <thead>
        <tr>
            <th>${ _('Transaction reference') }</th>
            <th>${ _('Description') }</th>
            <th>${ _('Invoice date') }</th>
            <th>${ _('Currency') }</th>
            <th>${ _('Debit/Credit') }</th>
            <th class="amount">${ _('Amount') }</th>
        </tr>
    </thead>
    <tbody>
    	%for voucher in vouchers:
	        %for line in voucher.line_ids:
		        <tr class="line">
		            <td>${ line.name }</td>
		            <td>${ line.move_line_id.ref }</td>
		            <td>${ line.date_original }</td>
		            <td>${ line.currency_id.name }</td>
		            <td>${ debit_credit(line) }</td>
		            <td class="amount">${ formatLang(line.amount, currency_obj=voucher.currency_id) }</td>
		        </tr>
	        %endfor
        %endfor
    </tbody>
</table>

<h2 class="payment_suggestion_total">
	${ _('Total for %s:') % partner.name }
	${ formatLang(partner_total, currency_obj=vouchers[0].currency_id) }
</h2>

</div>

%endfor

<h2 class="payment_suggestion_bottom">
	${ _('Generated on %s') % date() }
</h2>

<h2 class="payment_suggestion_bottom">
	${ _('Signature:') }
</h2>

%endfor
