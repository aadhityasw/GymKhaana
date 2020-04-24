function validateAgreement()
{
    const iagree = document.getElementById('agreement');
    if(iagree.checked == true)
    {
        console.log('Submitting')
    }
    else
    {
        alert('You should accept the terms and conditions in order to proceed for registration.');
    }
}